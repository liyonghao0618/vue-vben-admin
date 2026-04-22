from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import session_scope
from app.models import (
    CallEvent,
    CallParticipant,
    CallSession,
    ChatAuditLog,
    ChatConversation,
    ChatConversationMember,
    ChatInstancePresence,
    ChatMessage,
    ChatUserRelation,
    ElderFamilyBinding,
    User,
)
from app.schemas.chat import (
    CallEventItem,
    CallParticipantItem,
    CallSessionItem,
    CallSignalEventRequest,
    ChatRelationshipItem,
    ChatConversationDetail,
    ChatConversationItem,
    ChatConversationMemberItem,
    ChatMessageItem,
    ChatSendMessageRequest,
    ChatUnreadSummary,
    ChatRecommendedContactItem,
    ChatUserSearchItem,
    CreateChatBlacklistRequest,
    CreateChatReportRequest,
    CreateCallSessionRequest,
    CreateConversationRequest,
    EndCallSessionRequest,
    MarkMessageReadRequest,
    OnlineStateItem,
    UpdateChatMuteRequest,
)
from app.schemas.user import UserProfile


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _message_preview(text: str) -> str:
    return " ".join(text.split())[:80]


def _pair_key(user_ids: list[str]) -> str:
    return ":".join(sorted(user_ids))


def _analyze_risk(text: str) -> dict[str, str]:
    rules = [
        (r"https?://|www\.", "medium", "risk_link", "消息中包含链接，需谨慎核验来源。"),
        (r"验证码|verification code|otp", "high", "verify_code", "对话涉及验证码索取，存在账号接管风险。"),
        (r"转账|汇款|打款|银行卡|收款码", "high", "transfer", "对话涉及转账或收款信息，需提高警惕。"),
        (r"刷单|返利|退款|客服|安全账户|公检法|涉案", "high", "impersonation", "命中常见诈骗诱导话术。"),
        (r"加微信|私聊|下载app|点击链接", "medium", "induction", "命中导流或诱导操作话术。"),
    ]
    matches = [item for item in rules if re.search(item[0], text, re.IGNORECASE)]
    if not matches:
        return {"risk_level": "low", "risk_category": "", "risk_reason": "", "risk_suggestion": ""}
    level, category, reason = next((item[1:] for item in matches if item[1] == "high"), matches[0][1:])
    return {
        "risk_level": level,
        "risk_category": category,
        "risk_reason": reason,
        "risk_suggestion": "请勿泄露验证码、转账或点击不明链接，必要时联系家人、社区或求助入口。",
    }


def _normalize_relation(session, owner_user_id: str, target_user_id: str) -> ChatUserRelation:
    relation = session.scalar(
        select(ChatUserRelation).where(
            ChatUserRelation.owner_user_id == owner_user_id,
            ChatUserRelation.target_user_id == target_user_id,
        )
    )
    if relation:
        return relation
    relation = ChatUserRelation(owner_user_id=owner_user_id, target_user_id=target_user_id)
    session.add(relation)
    session.flush()
    return relation


def _write_audit_log(
    session,
    *,
    actor_user_id: str | None,
    action: str,
    target_user_id: str | None = None,
    conversation_id: str | None = None,
    message_id: str | None = None,
    risk_level: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    settings = get_settings()
    if not settings.chat_audit_enabled:
        return
    session.add(
        ChatAuditLog(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            action=action,
            detail_json=json.dumps(detail, ensure_ascii=False) if detail else None,
            risk_level=risk_level,
        )
    )


def _ensure_chat_allowed(session, actor_user_id: str, target_user_id: str) -> None:
    actor = session.get(User, actor_user_id)
    target = session.get(User, target_user_id)
    if not actor or actor.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号不可发起聊天")
    if not target or target.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="对方账号当前不可聊天")

    blocked = session.scalar(
        select(ChatUserRelation).where(
            or_(
                and_(
                    ChatUserRelation.owner_user_id == actor_user_id,
                    ChatUserRelation.target_user_id == target_user_id,
                    ChatUserRelation.is_blocked.is_(True),
                ),
                and_(
                    ChatUserRelation.owner_user_id == target_user_id,
                    ChatUserRelation.target_user_id == actor_user_id,
                    ChatUserRelation.is_blocked.is_(True),
                ),
            )
        )
    )
    if blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前聊天对象不可达")


def _to_message_item(message: ChatMessage, current_user_id: str) -> ChatMessageItem:
    return ChatMessageItem(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_user_id=message.sender_user_id,
        sender_name=message.sender.display_name if message.sender else "",
        message_type=message.message_type,
        content_text=message.content_text,
        content_json=json.loads(message.content_json) if message.content_json else None,
        status=message.status,
        is_self=message.sender_user_id == current_user_id,
        delivered_at=message.delivered_at,
        read_by_all_at=message.read_by_all_at,
        risk_level=message.risk_level,
        risk_category=message.risk_category,
        risk_reason=message.risk_reason,
        risk_suggestion=message.risk_suggestion,
        created_at=message.created_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
    )


def _require_member(session, conversation_id: str, user_id: str) -> ChatConversationMember:
    member = session.scalar(
        select(ChatConversationMember)
        .where(
            ChatConversationMember.conversation_id == conversation_id,
            ChatConversationMember.user_id == user_id,
        )
        .options(selectinload(ChatConversationMember.conversation))
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在或无权访问")
    return member


def _to_call_item(call: CallSession) -> CallSessionItem:
    return CallSessionItem(
        id=call.id,
        conversation_id=call.conversation_id,
        initiator_user_id=call.initiator_user_id,
        receiver_user_id=call.receiver_user_id,
        call_type=call.call_type,
        status=call.status,
        started_at=call.started_at,
        answered_at=call.answered_at,
        ended_at=call.ended_at,
        ended_reason=call.ended_reason,
        duration_seconds=call.duration_seconds,
        participants=[
            CallParticipantItem(
                user_id=item.user_id,
                display_name=item.user.display_name if item.user else "",
                role=item.role,
                join_state=item.join_state,
                joined_at=item.joined_at,
                left_at=item.left_at,
            )
            for item in call.participants
        ],
        events=[
            CallEventItem(
                id=item.id,
                call_session_id=item.call_session_id,
                actor_user_id=item.actor_user_id,
                event_type=item.event_type,
                payload_json=json.loads(item.payload_json) if item.payload_json else None,
                created_at=item.created_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            )
            for item in sorted(call.events, key=lambda event: event.created_at)
        ],
    )


def _load_call_session(session, call_session_id: str) -> CallSession | None:
    return session.scalar(
        select(CallSession)
        .where(CallSession.id == call_session_id)
        .execution_options(populate_existing=True)
        .options(
            selectinload(CallSession.participants).selectinload(CallParticipant.user),
            selectinload(CallSession.events),
            selectinload(CallSession.conversation).selectinload(ChatConversation.members),
        )
    )


def _append_call_event(
    session, call: CallSession, *, actor_user_id: str | None, event_type: str, data: dict[str, Any] | None = None
) -> None:
    session.add(
        CallEvent(
            call_session_id=call.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            payload_json=json.dumps(data, ensure_ascii=False) if data else None,
        )
    )


def _write_call_summary_message(session, call: CallSession) -> None:
    if not call.ended_at:
        return
    summary_map = {
        "cancelled": "已取消通话",
        "rejected": "已拒接",
        "missed": "未接来电",
        "busy": "对方忙线中",
        "timeout": "呼叫超时",
        "failed": "通话失败",
        "ended": f"通话 {call.duration_seconds // 60:02d}:{call.duration_seconds % 60:02d}",
    }
    content_text = f"[通话记录] {summary_map.get(call.ended_reason or '', '通话结束')}"
    message = ChatMessage(
        conversation_id=call.conversation_id,
        sender_user_id=call.initiator_user_id,
        receiver_user_id=call.receiver_user_id,
        message_type="card",
        content=content_text,
        content_text=content_text,
        content_json=json.dumps(
            {
                "card_type": "call_record",
                "call_session_id": call.id,
                "call_type": call.call_type,
                "status": call.status,
                "ended_reason": call.ended_reason,
                "duration_seconds": call.duration_seconds,
            },
            ensure_ascii=False,
        ),
        status="sent",
        delivered_at=call.ended_at,
        risk_level="low",
    )
    session.add(message)
    session.flush()
    conversation = session.get(ChatConversation, call.conversation_id)
    if conversation:
        conversation.last_message_id = message.id
        conversation.last_message_preview = content_text
        conversation.last_message_at = call.ended_at
        for member in conversation.members:
            if member.user_id == call.initiator_user_id:
                member.last_read_message_id = message.id
                member.last_read_at = call.ended_at
            else:
                member.unread_count += 1


def _has_call_summary_message(session, call: CallSession) -> bool:
    return bool(
        session.scalar(
            select(ChatMessage.id).where(
                ChatMessage.conversation_id == call.conversation_id,
                ChatMessage.content_json.like(f'%\"call_session_id\": \"{call.id}\"%'),
            )
        )
    )


def _to_online_state_item(
    *,
    user_id: str,
    is_online: bool,
    last_seen_at: str | None = None,
    client_type: str | None = None,
) -> OnlineStateItem:
    return OnlineStateItem(
        user_id=user_id,
        is_online=is_online,
        last_seen_at=last_seen_at,
        client_type=client_type,
    )


def _list_presence_subscriber_ids(session, user_id: str) -> list[str]:
    conversation_ids = select(ChatConversationMember.conversation_id).where(
        ChatConversationMember.user_id == user_id
    )
    return (
        session.execute(
            select(ChatConversationMember.user_id)
            .where(
                ChatConversationMember.conversation_id.in_(conversation_ids),
                ChatConversationMember.user_id != user_id,
            )
            .distinct()
        )
        .scalars()
        .all()
    )


def _expire_stale_pending_calls(session, participant_user_ids: list[str]) -> None:
    settings = get_settings()
    timeout_seconds = max(settings.call_session_invite_timeout_seconds, 0)
    if timeout_seconds <= 0:
        return

    now = _now()
    now_dt = _parse_datetime(now)
    assert now_dt is not None
    calls = (
        session.execute(
            select(CallSession)
            .where(
                CallSession.status.in_(["initiated", "ringing"]),
                or_(
                    CallSession.initiator_user_id.in_(participant_user_ids),
                    CallSession.receiver_user_id.in_(participant_user_ids),
                ),
            )
            .options(
                selectinload(CallSession.participants),
                selectinload(CallSession.conversation).selectinload(ChatConversation.members),
                selectinload(CallSession.events),
            )
        )
        .scalars()
        .all()
    )

    for call in calls:
        started_at = _parse_datetime(call.started_at) or call.created_at.astimezone(UTC)
        if (now_dt - started_at).total_seconds() < timeout_seconds:
            continue
        call.status = "timeout"
        call.ended_reason = "timeout"
        call.ended_at = now
        for participant in call.participants:
            participant.left_at = now
            if participant.join_state in {"invited", "joined", "ringing"}:
                participant.join_state = "left"
        _append_call_event(
            session,
            call,
            actor_user_id=None,
            event_type="call.timeout",
            data={"reason": "stale_timeout", "timeout_seconds": timeout_seconds},
        )
        if not _has_call_summary_message(session, call):
            _write_call_summary_message(session, call)
    session.flush()


def end_disconnected_active_calls(user: UserProfile) -> list[CallSessionItem]:
    with session_scope() as session:
        calls = (
            session.execute(
                select(CallSession)
                .where(
                    CallSession.status == "accepted",
                    or_(
                        CallSession.initiator_user_id == user.user_id,
                        CallSession.receiver_user_id == user.user_id,
                    ),
                )
                .options(
                    selectinload(CallSession.participants).selectinload(CallParticipant.user),
                    selectinload(CallSession.events),
                    selectinload(CallSession.conversation).selectinload(ChatConversation.members),
                )
            )
            .scalars()
            .all()
        )
        if not calls:
            return []

        now = _now()
        disconnected_calls: list[CallSessionItem] = []
        for call in calls:
            call.status = "failed"
            call.ended_reason = "failed"
            call.ended_at = now
            if call.answered_at:
                answered_dt = datetime.fromisoformat(call.answered_at.replace("Z", "+00:00"))
                ended_dt = datetime.fromisoformat(call.ended_at.replace("Z", "+00:00"))
                call.duration_seconds = max(int((ended_dt - answered_dt).total_seconds()), 0)
            for participant in call.participants:
                participant.left_at = now
                if participant.join_state in {"invited", "joined", "ringing"}:
                    participant.join_state = "left"
            _append_call_event(
                session,
                call,
                actor_user_id=user.user_id,
                event_type="call.end",
                data={"reason": "failed", "source": "disconnect"},
            )
            if not _has_call_summary_message(session, call):
                _write_call_summary_message(session, call)
            session.flush()
            session.expire(call, ["conversation", "events", "participants"])
            refreshed_call = _load_call_session(session, call.id)
            assert refreshed_call is not None
            disconnected_calls.append(_to_call_item(refreshed_call))
        return disconnected_calls


def search_chat_users(user: UserProfile, keyword: str | None = None, limit: int = 20) -> list[ChatUserSearchItem]:
    with session_scope() as session:
        blocked_subquery = select(ChatUserRelation.target_user_id).where(
            ChatUserRelation.owner_user_id == user.user_id,
            ChatUserRelation.is_blocked.is_(True),
        )
        query = select(User).where(User.id != user.user_id, User.status == "active").order_by(User.display_name.asc())
        query = query.where(User.id.not_in(blocked_subquery))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(or_(User.display_name.ilike(pattern), User.username.ilike(pattern), User.phone.ilike(pattern)))
        rows = session.execute(query.limit(limit)).scalars().all()
        return [
            ChatUserSearchItem(
                user_id=item.id,
                username=item.username,
                display_name=item.display_name,
                phone=item.phone,
                status=item.status,
            )
            for item in rows
        ]


def list_recommended_contacts(user: UserProfile, limit: int = 10) -> list[ChatRecommendedContactItem]:
    with session_scope() as session:
        blocked_subquery = select(ChatUserRelation.target_user_id).where(
            ChatUserRelation.owner_user_id == user.user_id,
            ChatUserRelation.is_blocked.is_(True),
        )
        query = (
            select(ElderFamilyBinding, User)
            .join(
                User,
                or_(
                    and_(
                        ElderFamilyBinding.elder_user_id == user.user_id,
                        ElderFamilyBinding.family_user_id == User.id,
                    ),
                    and_(
                        ElderFamilyBinding.family_user_id == user.user_id,
                        ElderFamilyBinding.elder_user_id == User.id,
                    ),
                ),
            )
            .where(
                ElderFamilyBinding.status == "active",
                User.id != user.user_id,
                User.status == "active",
                User.id.not_in(blocked_subquery),
            )
            .order_by(ElderFamilyBinding.is_emergency_contact.desc(), ElderFamilyBinding.created_at.desc())
            .limit(limit)
        )
        rows = session.execute(query).all()
        return [
            ChatRecommendedContactItem(
                user_id=target.id,
                username=target.username,
                display_name=target.display_name,
                phone=target.phone,
                status=target.status,
                relationship_type=binding.relationship_type,
                is_emergency_contact=binding.is_emergency_contact,
                recommendation_reason=(
                    f"来自已绑定{binding.relationship_type or '家庭'}关系"
                    + ("，且为紧急联系人" if binding.is_emergency_contact else "")
                ),
            )
            for binding, target in rows
        ]


def create_or_get_conversation(user: UserProfile, payload: CreateConversationRequest) -> ChatConversationDetail:
    participant_ids = sorted(set([user.user_id, *payload.participant_user_ids]))
    with session_scope() as session:
        users = session.execute(select(User).where(User.id.in_(participant_ids), User.status == "active")).scalars().all()
        if len(users) != 2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话成员不存在或不可达")
        peer_user_id = next(item for item in participant_ids if item != user.user_id)
        _ensure_chat_allowed(session, user.user_id, peer_user_id)

        conversation_rows = (
            session.execute(
                select(ChatConversation)
                .join(ChatConversationMember)
                .where(ChatConversation.conversation_type == "direct")
                .options(
                    selectinload(ChatConversation.members).selectinload(ChatConversationMember.user),
                    selectinload(ChatConversation.messages).selectinload(ChatMessage.sender),
                )
            )
            .scalars()
            .unique()
            .all()
        )
        for conversation in conversation_rows:
            if sorted(member.user_id for member in conversation.members) == participant_ids:
                return get_conversation_detail(user, conversation.id)

        now = _now()
        conversation = ChatConversation(
            conversation_type="direct",
            pair_key=_pair_key(participant_ids),
            title=payload.title,
        )
        session.add(conversation)
        session.flush()
        for participant_id in participant_ids:
            session.add(
                ChatConversationMember(
                    conversation_id=conversation.id,
                    user_id=participant_id,
                    role_code="member",
                    joined_at=now,
                )
            )
        session.flush()
        conversation_id = conversation.id
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="conversation_created",
            target_user_id=peer_user_id,
            conversation_id=conversation_id,
            detail={"conversation_type": payload.conversation_type},
        )
    return get_conversation_detail(user, conversation_id)


def list_conversations(user: UserProfile) -> list[ChatConversationItem]:
    with session_scope() as session:
        rows = (
            session.execute(
                select(ChatConversationMember)
                .where(ChatConversationMember.user_id == user.user_id)
                .options(
                    selectinload(ChatConversationMember.conversation)
                    .selectinload(ChatConversation.members)
                    .selectinload(ChatConversationMember.user)
                )
            )
            .scalars()
            .all()
        )
        result: list[ChatConversationItem] = []
        for member in rows:
            conversation = member.conversation
            peer_member = next((item for item in conversation.members if item.user_id != user.user_id), None)
            peer = peer_member.user if peer_member else None
            result.append(
                ChatConversationItem(
                    id=conversation.id,
                    conversation_type=conversation.conversation_type,
                    title=conversation.title or (peer.display_name if peer else "聊天会话"),
                    peer_user_id=peer.id if peer else None,
                    peer_name=peer.display_name if peer else None,
                    peer_status=peer.status if peer else None,
                    unread_count=member.unread_count,
                    last_message_preview=conversation.last_message_preview,
                    last_message_at=conversation.last_message_at,
                    last_message_id=conversation.last_message_id,
                )
            )
        result.sort(key=lambda item: item.last_message_at or "", reverse=True)
        return result


def get_conversation_detail(
    user: UserProfile, conversation_id: str, page: int = 1, page_size: int = 20
) -> ChatConversationDetail:
    with session_scope() as session:
        member = _require_member(session, conversation_id, user.user_id)
        conversation = session.scalar(
            select(ChatConversation)
            .where(ChatConversation.id == conversation_id)
            .options(
                selectinload(ChatConversation.members).selectinload(ChatConversationMember.user),
                selectinload(ChatConversation.messages).selectinload(ChatMessage.sender),
            )
        )
        assert conversation is not None
        peer_member = next((item for item in conversation.members if item.user_id != user.user_id), None)
        peer = peer_member.user if peer_member else None
        messages = sorted(conversation.messages, key=lambda item: item.created_at)
        total = len(messages)
        start = max(total - page * page_size, 0)
        end = total - (page - 1) * page_size
        selected = messages[start:end]
        return ChatConversationDetail(
            id=conversation.id,
            conversation_type=conversation.conversation_type,
            title=conversation.title or (peer.display_name if peer else "聊天会话"),
            peer_user_id=peer.id if peer else None,
            peer_name=peer.display_name if peer else None,
            peer_status=peer.status if peer else None,
            unread_count=member.unread_count,
            last_message_preview=conversation.last_message_preview,
            last_message_at=conversation.last_message_at,
            last_message_id=conversation.last_message_id,
            members=[
                ChatConversationMemberItem(
                    user_id=item.user_id,
                    display_name=item.user.display_name if item.user else "",
                    status=item.user.status if item.user else "",
                    joined_at=item.joined_at,
                    last_read_message_id=item.last_read_message_id,
                    last_read_at=item.last_read_at,
                    unread_count=item.unread_count,
                )
                for item in conversation.members
            ],
            messages=[_to_message_item(item, user.user_id) for item in selected],
            pagination={"page": page, "page_size": page_size, "total": total},
        )


def send_message(user: UserProfile, conversation_id: str, payload: ChatSendMessageRequest) -> ChatMessageItem:
    if payload.message_type != "text":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="一期仅支持文本消息")

    with session_scope() as session:
        _require_member(session, conversation_id, user.user_id)
        conversation = session.scalar(
            select(ChatConversation)
            .where(ChatConversation.id == conversation_id)
            .options(selectinload(ChatConversation.members))
        )
        assert conversation is not None
        peer_member = next((item for item in conversation.members if item.user_id != user.user_id), None)
        if peer_member:
            _ensure_chat_allowed(session, user.user_id, peer_member.user_id)
        now = _now()
        risk = _analyze_risk(payload.content_text)
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_user_id=user.user_id,
            receiver_user_id=peer_member.user_id if peer_member else user.user_id,
            message_type=payload.message_type,
            content=payload.content_text,
            content_text=payload.content_text,
            content_json=json.dumps(payload.content_json, ensure_ascii=False) if payload.content_json else None,
            status="sent",
            delivered_at=now,
            risk_level=risk["risk_level"],
            risk_category=risk["risk_category"] or None,
            risk_reason=risk["risk_reason"] or None,
            risk_suggestion=risk["risk_suggestion"] or None,
        )
        session.add(message)
        session.flush()
        conversation.last_message_id = message.id
        conversation.last_message_preview = _message_preview(payload.content_text)
        conversation.last_message_at = now
        for member in conversation.members:
            if member.user_id == user.user_id:
                member.last_read_message_id = message.id
                member.last_read_at = now
                member.unread_count = 0
            else:
                member.unread_count += 1
        session.refresh(message, attribute_names=["sender"])
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="message_sent",
            target_user_id=peer_member.user_id if peer_member else None,
            conversation_id=conversation_id,
            message_id=message.id,
            risk_level=message.risk_level,
            detail={"message_type": payload.message_type, "content_preview": _message_preview(payload.content_text)},
        )
        return _to_message_item(message, user.user_id)


def mark_messages_read(user: UserProfile, conversation_id: str, payload: MarkMessageReadRequest) -> ChatUnreadSummary:
    with session_scope() as session:
        member = _require_member(session, conversation_id, user.user_id)
        now = _now()
        member.last_read_message_id = payload.last_read_message_id
        member.last_read_at = now
        member.unread_count = 0
        latest_message = session.get(ChatMessage, payload.last_read_message_id)
        if latest_message:
            latest_message.read_at = now
            latest_message.read_by_all_at = now
        session.flush()
        total_unread = session.scalar(
            select(func.sum(ChatConversationMember.unread_count)).where(ChatConversationMember.user_id == user.user_id)
        )
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="message_read",
            conversation_id=conversation_id,
            message_id=payload.last_read_message_id,
            detail={"total_unread": total_unread or 0},
        )
        return ChatUnreadSummary(total_unread=total_unread or 0)


def get_unread_summary(user: UserProfile) -> ChatUnreadSummary:
    with session_scope() as session:
        total_unread = session.scalar(
            select(func.sum(ChatConversationMember.unread_count)).where(ChatConversationMember.user_id == user.user_id)
        )
        return ChatUnreadSummary(total_unread=total_unread or 0)


def list_online_states(user: UserProfile, user_ids: list[str] | None = None) -> list[OnlineStateItem]:
    target_ids = user_ids or [user.user_id]
    with session_scope() as session:
        rows = session.execute(
            select(ChatInstancePresence).where(ChatInstancePresence.user_id.in_(target_ids))
        ).scalars().all()
        row_map = {row.user_id: row for row in rows}
        return [
            _to_online_state_item(
                user_id=item,
                is_online=item in row_map,
                last_seen_at=row_map[item].last_seen_at if item in row_map else None,
                client_type=row_map[item].client_type if item in row_map else None,
            )
            for item in target_ids
        ]


def list_relationships(user: UserProfile) -> list[ChatRelationshipItem]:
    with session_scope() as session:
        rows = session.execute(
            select(ChatUserRelation).where(
                ChatUserRelation.owner_user_id == user.user_id,
                or_(ChatUserRelation.is_blocked.is_(True), ChatUserRelation.is_reported.is_(True)),
            )
        ).scalars().all()
        return [
            ChatRelationshipItem(
                target_user_id=item.target_user_id,
                is_blocked=item.is_blocked,
                is_reported=item.is_reported,
                report_reason=item.report_reason,
                blocked_at=item.blocked_at,
                reported_at=item.reported_at,
            )
            for item in rows
        ]


def create_blacklist_record(user: UserProfile, payload: CreateChatBlacklistRequest) -> ChatRelationshipItem:
    if payload.target_user_id == user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能将自己加入黑名单")
    with session_scope() as session:
        _ensure_chat_allowed(session, user.user_id, payload.target_user_id)
        relation = _normalize_relation(session, user.user_id, payload.target_user_id)
        relation.is_blocked = True
        relation.blocked_at = _now()
        if payload.reason:
            relation.report_reason = payload.reason
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="user_blocked",
            target_user_id=payload.target_user_id,
            detail={"reason": payload.reason},
        )
        return ChatRelationshipItem(
            target_user_id=relation.target_user_id,
            is_blocked=relation.is_blocked,
            is_reported=relation.is_reported,
            report_reason=relation.report_reason,
            blocked_at=relation.blocked_at,
            reported_at=relation.reported_at,
        )


def remove_blacklist_record(user: UserProfile, target_user_id: str) -> ChatRelationshipItem:
    with session_scope() as session:
        relation = _normalize_relation(session, user.user_id, target_user_id)
        relation.is_blocked = False
        relation.blocked_at = None
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="user_unblocked",
            target_user_id=target_user_id,
        )
        return ChatRelationshipItem(
            target_user_id=relation.target_user_id,
            is_blocked=relation.is_blocked,
            is_reported=relation.is_reported,
            report_reason=relation.report_reason,
            blocked_at=relation.blocked_at,
            reported_at=relation.reported_at,
        )


def create_report_record(user: UserProfile, payload: CreateChatReportRequest) -> ChatRelationshipItem:
    if payload.target_user_id == user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能举报自己")
    with session_scope() as session:
        relation = _normalize_relation(session, user.user_id, payload.target_user_id)
        relation.is_reported = True
        relation.report_reason = payload.reason
        relation.reported_at = _now()
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="user_reported",
            target_user_id=payload.target_user_id,
            conversation_id=payload.conversation_id,
            message_id=payload.message_id,
            detail={"reason": payload.reason},
        )
        return ChatRelationshipItem(
            target_user_id=relation.target_user_id,
            is_blocked=relation.is_blocked,
            is_reported=relation.is_reported,
            report_reason=relation.report_reason,
            blocked_at=relation.blocked_at,
            reported_at=relation.reported_at,
        )


def update_conversation_mute(
    user: UserProfile, conversation_id: str, payload: UpdateChatMuteRequest
) -> ChatConversationMemberItem:
    with session_scope() as session:
        member = _require_member(session, conversation_id, user.user_id)
        member.is_muted = payload.is_muted
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="conversation_muted" if payload.is_muted else "conversation_unmuted",
            conversation_id=conversation_id,
        )
        session.refresh(member, attribute_names=["user"])
        return ChatConversationMemberItem(
            user_id=member.user_id,
            display_name=member.user.display_name if member.user else "",
            status=member.user.status if member.user else "",
            joined_at=member.joined_at,
            last_read_message_id=member.last_read_message_id,
            last_read_at=member.last_read_at,
            unread_count=member.unread_count,
        )


def create_call_session(user: UserProfile, payload: CreateCallSessionRequest) -> CallSessionItem:
    with session_scope() as session:
        member = _require_member(session, payload.conversation_id, user.user_id)
        conversation = session.scalar(
            select(ChatConversation)
            .where(ChatConversation.id == payload.conversation_id)
            .options(
                selectinload(ChatConversation.members).selectinload(ChatConversationMember.user),
                selectinload(ChatConversation.messages).selectinload(ChatMessage.sender),
            )
        )
        assert conversation is not None
        if conversation.conversation_type != "direct" or len(conversation.members) != 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="一期仅支持一对一通话")
        peer_member = next((item for item in conversation.members if item.user_id != user.user_id), None)
        if not peer_member:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前会话缺少被叫成员")
        _ensure_chat_allowed(session, user.user_id, peer_member.user_id)
        _expire_stale_pending_calls(session, [user.user_id, peer_member.user_id])

        active_call = session.scalar(
            select(CallSession).where(
                CallSession.status.in_(["initiated", "ringing", "accepted"]),
                or_(
                    CallSession.initiator_user_id.in_([user.user_id, peer_member.user_id]),
                    CallSession.receiver_user_id.in_([user.user_id, peer_member.user_id]),
                ),
            )
        )
        if active_call:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前存在进行中的通话")

        now = _now()
        call = CallSession(
            conversation_id=conversation.id,
            initiator_user_id=user.user_id,
            receiver_user_id=peer_member.user_id,
            call_type=payload.call_type,
            status="initiated",
            started_at=now,
        )
        session.add(call)
        session.flush()
        session.add_all(
            [
                CallParticipant(
                    call_session_id=call.id,
                    user_id=user.user_id,
                    role="initiator",
                    join_state="joined",
                    joined_at=now,
                ),
                CallParticipant(
                    call_session_id=call.id,
                    user_id=peer_member.user_id,
                    role="receiver",
                    join_state="invited",
                ),
            ]
        )
        _append_call_event(
            session,
            call,
            actor_user_id=user.user_id,
            event_type="call.invite",
            data={"conversation_id": conversation.id, "call_type": payload.call_type},
        )
        _write_audit_log(
            session,
            actor_user_id=user.user_id,
            action="call_created",
            target_user_id=peer_member.user_id,
            conversation_id=conversation.id,
            detail={"call_session_id": call.id, "call_type": payload.call_type},
        )
        session.flush()
        call = session.scalar(
            select(CallSession)
            .where(CallSession.id == call.id)
            .options(
                selectinload(CallSession.participants).selectinload(CallParticipant.user),
                selectinload(CallSession.events),
            )
        )
        assert call is not None
        return _to_call_item(call)


def get_call_session_detail(user: UserProfile, call_session_id: str) -> CallSessionItem:
    with session_scope() as session:
        call = _load_call_session(session, call_session_id)
        if not call or user.user_id not in {call.initiator_user_id, call.receiver_user_id}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通话不存在或无权访问")
        return _to_call_item(call)


def list_call_history(user: UserProfile, conversation_id: str | None = None) -> list[CallSessionItem]:
    with session_scope() as session:
        query = select(CallSession).where(
            or_(CallSession.initiator_user_id == user.user_id, CallSession.receiver_user_id == user.user_id)
        )
        if conversation_id:
            query = query.where(CallSession.conversation_id == conversation_id)
        rows = (
            session.execute(
                query.options(
                    selectinload(CallSession.participants).selectinload(CallParticipant.user),
                    selectinload(CallSession.events),
                )
            )
            .scalars()
            .all()
        )
        rows.sort(key=lambda item: item.created_at, reverse=True)
        return [_to_call_item(item) for item in rows]


def end_call_session(user: UserProfile, call_session_id: str, payload: EndCallSessionRequest) -> CallSessionItem:
    with session_scope() as session:
        call = _load_call_session(session, call_session_id)
        if not call or user.user_id not in {call.initiator_user_id, call.receiver_user_id}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通话不存在或无权访问")
        if call.status not in {"accepted", "initiated", "ringing"}:
            return _to_call_item(call)
        call.status = "ended" if payload.reason == "ended" else payload.reason
        call.ended_reason = payload.reason
        call.ended_at = _now()
        if call.answered_at:
            answered_dt = datetime.fromisoformat(call.answered_at.replace("Z", "+00:00"))
            ended_dt = datetime.fromisoformat(call.ended_at.replace("Z", "+00:00"))
            call.duration_seconds = max(int((ended_dt - answered_dt).total_seconds()), 0)
        for participant in call.participants:
            participant.left_at = call.ended_at
            if participant.join_state in {"invited", "joined"}:
                participant.join_state = "left"
        _append_call_event(session, call, actor_user_id=user.user_id, event_type="call.end", data={"reason": payload.reason})
        _write_call_summary_message(session, call)
        session.flush()
        session.expire(call, ["conversation", "events", "participants"])
        refreshed_call = _load_call_session(session, call.id)
        assert refreshed_call is not None
        return _to_call_item(refreshed_call)


def handle_call_signal(user: UserProfile, payload: CallSignalEventRequest) -> tuple[CallSessionItem, str]:
    with session_scope() as session:
        call = _load_call_session(session, payload.call_session_id)
        if not call or user.user_id not in {call.initiator_user_id, call.receiver_user_id}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通话不存在或无权访问")
        now = _now()
        data = payload.data or {}
        if payload.event == "call.ringing":
            call.status = "ringing"
        elif payload.event == "call.accept":
            call.status = "accepted"
            call.answered_at = now
        elif payload.event in {"call.reject", "call.busy", "call.timeout"}:
            reason = payload.event.split(".")[1]
            call.status = "rejected" if reason == "reject" else reason
            call.ended_reason = "rejected" if reason == "reject" else reason
            call.ended_at = now
        elif payload.event == "call.end":
            call.status = "ended"
            call.ended_reason = data.get("reason", "ended")
            call.ended_at = now
            if call.answered_at:
                answered_dt = datetime.fromisoformat(call.answered_at.replace("Z", "+00:00"))
                ended_dt = datetime.fromisoformat(call.ended_at.replace("Z", "+00:00"))
                call.duration_seconds = max(int((ended_dt - answered_dt).total_seconds()), 0)
        elif payload.event == "call.offer":
            call.offer_sdp = json.dumps(data, ensure_ascii=False)
        elif payload.event == "call.answer":
            call.answer_sdp = json.dumps(data, ensure_ascii=False)
        elif payload.event == "call.ice-candidate":
            call.last_ice_candidate = json.dumps(data, ensure_ascii=False)

        for participant in call.participants:
            if participant.user_id == user.user_id and payload.event in {"call.accept", "call.ringing"}:
                participant.join_state = "joined" if payload.event == "call.accept" else "ringing"
                participant.joined_at = participant.joined_at or now
            elif participant.user_id == user.user_id and payload.event in {"call.reject", "call.end", "call.busy", "call.timeout"}:
                participant.join_state = "left"
                participant.left_at = now

        _append_call_event(session, call, actor_user_id=user.user_id, event_type=payload.event, data=data)
        if call.ended_at and not session.scalar(
            select(ChatMessage.id).where(
                ChatMessage.conversation_id == call.conversation_id,
                ChatMessage.content_json.like(f'%\"call_session_id\": \"{call.id}\"%'),
            )
        ):
            _write_call_summary_message(session, call)
        session.flush()
        session.expire(call, ["conversation", "events", "participants"])
        refreshed_call = _load_call_session(session, call.id)
        assert refreshed_call is not None
        return _to_call_item(refreshed_call), call.conversation_id


class ChatMessageRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, user_id: str) -> None:
        settings = get_settings()
        limit = settings.chat_message_rate_limit_count
        window = settings.chat_message_rate_limit_window_seconds
        if limit <= 0 or window <= 0:
            return
        now = datetime.now(UTC).timestamp()
        bucket = self._events[user_id]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"发送过于频繁，请在 {window} 秒后重试",
            )
        bucket.append(now)


rate_limiter = ChatMessageRateLimiter()


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, user: UserProfile, websocket: WebSocket) -> str:
        connection_id = str(uuid4())
        await websocket.accept()
        self.active_connections.setdefault(user.user_id, {})[connection_id] = websocket
        now = _now()
        with session_scope() as session:
            existing = session.scalar(
                select(ChatInstancePresence).where(ChatInstancePresence.user_id == user.user_id)
            )
            if existing:
                existing.connection_id = connection_id
                existing.status = "online"
                existing.last_seen_at = now
                existing.client_type = "web"
            else:
                session.add(
                    ChatInstancePresence(
                        user_id=user.user_id,
                        connection_id=connection_id,
                        status="online",
                        last_seen_at=now,
                        client_type="web",
                    )
                )
        return connection_id

    def disconnect(self, user: UserProfile, connection_id: str) -> bool:
        sockets = self.active_connections.get(user.user_id, {})
        sockets.pop(connection_id, None)
        has_remaining_connections = bool(sockets)
        if not has_remaining_connections:
            self.active_connections.pop(user.user_id, None)
        now = _now()
        with session_scope() as session:
            presence = session.scalar(select(ChatInstancePresence).where(ChatInstancePresence.user_id == user.user_id))
            if presence:
                if has_remaining_connections:
                    presence.connection_id = next(iter(sockets))
                    presence.status = "online"
                    presence.last_seen_at = now
                    presence.client_type = "web"
                else:
                    presence.last_seen_at = now
                    session.delete(presence)
        return not has_remaining_connections

    async def send_to_user(self, user_id: str, payload: dict[str, Any]) -> None:
        for websocket in self.active_connections.get(user_id, {}).values():
            await websocket.send_json(payload)

    async def broadcast_to_conversation(self, conversation_id: str, payload: dict[str, Any]) -> None:
        with session_scope() as session:
            member_ids = session.execute(
                select(ChatConversationMember.user_id).where(ChatConversationMember.conversation_id == conversation_id)
            ).scalars().all()
        for user_id in member_ids:
            await self.send_to_user(user_id, payload)

    async def broadcast_presence(
        self,
        user_id: str,
        *,
        is_online: bool,
        last_seen_at: str | None = None,
        client_type: str | None = None,
    ) -> None:
        with session_scope() as session:
            subscriber_ids = _list_presence_subscriber_ids(session, user_id)
        if not subscriber_ids:
            return
        payload = {
            "event": "presence",
            "data": _to_online_state_item(
                user_id=user_id,
                is_online=is_online,
                last_seen_at=last_seen_at,
                client_type=client_type,
            ).model_dump(),
        }
        for subscriber_id in subscriber_ids:
            await self.send_to_user(subscriber_id, payload)


manager = ChatConnectionManager()


async def websocket_loop(user: UserProfile, websocket: WebSocket) -> None:
    connection_id = await manager.connect(user, websocket)
    connected_at = _now()
    await manager.send_to_user(
        user.user_id, {"event": "connected", "data": {"connection_id": connection_id, "user_id": user.user_id}}
    )
    await manager.broadcast_presence(
        user.user_id,
        is_online=True,
        last_seen_at=connected_at,
        client_type="web",
    )
    try:
        while True:
            payload = await websocket.receive_json()
            event = payload.get("event")
            if event == "ping":
                with session_scope() as session:
                    presence = session.scalar(
                        select(ChatInstancePresence).where(ChatInstancePresence.connection_id == connection_id)
                    )
                    if presence:
                        presence.last_seen_at = _now()
                await websocket.send_json({"event": "pong", "data": {"ts": _now()}})
            elif event == "typing":
                conversation_id = payload.get("data", {}).get("conversation_id")
                if conversation_id:
                    await manager.broadcast_to_conversation(
                        conversation_id,
                        {
                            "event": "typing",
                            "data": {
                                "conversation_id": conversation_id,
                                "user_id": user.user_id,
                                "display_name": user.display_name,
                            },
                        },
                    )
            elif event and event.startswith("call."):
                call_state, conversation_id = handle_call_signal(
                    user,
                    CallSignalEventRequest(
                        event=event,
                        call_session_id=payload.get("data", {}).get("call_session_id", ""),
                        data=payload.get("data"),
                    ),
                )
                await manager.broadcast_to_conversation(
                    conversation_id,
                    {
                        "event": event,
                        "data": call_state.model_dump(),
                    },
                )
    except WebSocketDisconnect:
        pass
    finally:
        disconnected_at = _now()
        user_went_offline = manager.disconnect(user, connection_id)
        if user_went_offline:
            disconnected_calls = end_disconnected_active_calls(user)
            await manager.broadcast_presence(
                user.user_id,
                is_online=False,
                last_seen_at=disconnected_at,
            )
            for call in disconnected_calls:
                await manager.broadcast_to_conversation(
                    call.conversation_id,
                    {
                        "event": "call.end",
                        "data": call.model_dump(),
                    },
                )
