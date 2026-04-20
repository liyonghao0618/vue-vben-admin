from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.db.session import session_scope
from app.models import ChatConversation, ChatConversationMember, ChatInstancePresence, ChatMessage, User
from app.schemas.chat import (
    ChatConversationDetail,
    ChatConversationItem,
    ChatConversationMemberItem,
    ChatMessageItem,
    ChatSendMessageRequest,
    ChatUnreadSummary,
    ChatUserSearchItem,
    CreateConversationRequest,
    MarkMessageReadRequest,
    OnlineStateItem,
)
from app.schemas.user import UserProfile


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _message_preview(text: str) -> str:
    return " ".join(text.split())[:80]


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


def search_chat_users(user: UserProfile, keyword: str | None = None, limit: int = 20) -> list[ChatUserSearchItem]:
    with session_scope() as session:
        query = select(User).where(User.id != user.user_id, User.status == "active").order_by(User.display_name.asc())
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


def create_or_get_conversation(user: UserProfile, payload: CreateConversationRequest) -> ChatConversationDetail:
    participant_ids = sorted(set([user.user_id, *payload.participant_user_ids]))
    with session_scope() as session:
        users = session.execute(select(User).where(User.id.in_(participant_ids), User.status == "active")).scalars().all()
        if len(users) != 2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话成员不存在或不可达")

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
        conversation = ChatConversation(conversation_type="direct", title=payload.title)
        session.add(conversation)
        session.flush()
        for participant_id in participant_ids:
            session.add(ChatConversationMember(conversation_id=conversation.id, user_id=participant_id, joined_at=now))
        session.flush()
        conversation_id = conversation.id
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
        now = _now()
        risk = _analyze_risk(payload.content_text)
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_user_id=user.user_id,
            message_type=payload.message_type,
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
            latest_message.read_by_all_at = now
        session.flush()
        total_unread = session.scalar(
            select(func.sum(ChatConversationMember.unread_count)).where(ChatConversationMember.user_id == user.user_id)
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
        rows = session.execute(select(ChatInstancePresence).where(ChatInstancePresence.user_id.in_(target_ids))).scalars().all()
        row_map = {row.user_id: row for row in rows}
        return [
            OnlineStateItem(
                user_id=item,
                is_online=item in row_map,
                last_seen_at=row_map[item].last_seen_at if item in row_map else None,
                client_type=row_map[item].client_type if item in row_map else None,
            )
            for item in target_ids
        ]


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user: UserProfile, websocket: WebSocket) -> str:
        await websocket.accept()
        self.active_connections.setdefault(user.user_id, []).append(websocket)
        connection_id = str(uuid4())
        with session_scope() as session:
            existing = session.scalar(select(ChatInstancePresence).where(ChatInstancePresence.user_id == user.user_id))
            if existing:
                existing.connection_id = connection_id
                existing.status = "online"
                existing.last_seen_at = _now()
            else:
                session.add(
                    ChatInstancePresence(
                        user_id=user.user_id,
                        connection_id=connection_id,
                        status="online",
                        last_seen_at=_now(),
                        client_type="web",
                    )
                )
        return connection_id

    def disconnect(self, user: UserProfile, websocket: WebSocket, connection_id: str) -> None:
        sockets = self.active_connections.get(user.user_id, [])
        self.active_connections[user.user_id] = [item for item in sockets if item is not websocket]
        if not self.active_connections[user.user_id]:
            self.active_connections.pop(user.user_id, None)
        with session_scope() as session:
            presence = session.scalar(
                select(ChatInstancePresence).where(
                    and_(ChatInstancePresence.user_id == user.user_id, ChatInstancePresence.connection_id == connection_id)
                )
            )
            if presence:
                session.delete(presence)

    async def send_to_user(self, user_id: str, payload: dict[str, Any]) -> None:
        for websocket in self.active_connections.get(user_id, []):
            await websocket.send_json(payload)

    async def broadcast_to_conversation(self, conversation_id: str, payload: dict[str, Any]) -> None:
        with session_scope() as session:
            member_ids = session.execute(
                select(ChatConversationMember.user_id).where(ChatConversationMember.conversation_id == conversation_id)
            ).scalars().all()
        for user_id in member_ids:
            await self.send_to_user(user_id, payload)


manager = ChatConnectionManager()


async def websocket_loop(user: UserProfile, websocket: WebSocket) -> None:
    connection_id = await manager.connect(user, websocket)
    await manager.send_to_user(
        user.user_id, {"event": "connected", "data": {"connection_id": connection_id, "user_id": user.user_id}}
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
    except WebSocketDisconnect:
        manager.disconnect(user, websocket, connection_id)
