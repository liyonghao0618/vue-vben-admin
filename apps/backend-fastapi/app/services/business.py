from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import aliased, selectinload

from app.constants.roles import UserRole
from app.db.session import session_scope
from app.models import (
    CallRecognitionRecord,
    EducationContent,
    ElderFamilyBinding,
    NotificationRecord,
    PromptTemplate,
    Role,
    RiskAlert,
    RiskRule,
    SystemConfig,
    User,
    UserRoleLink,
    Workorder,
    WorkorderAction,
    SmsRecognitionRecord,
)
from app.schemas.business import (
    AdminUserItem,
    AccessibilitySettings,
    AccessibilitySettingsUpdateRequest,
    BindingCreateRequest,
    BindingItem,
    BindingUpdateRequest,
    CommunityReportData,
    ContentUpsertRequest,
    CommunityElderItem,
    ContentItem,
    EducationContentItem,
    FamilyReminderCreateRequest,
    FamilyReminderResult,
    HelpRequestCreate,
    HelpRequestResult,
    NotificationItem,
    NotificationReadResult,
    PaginationMeta,
    PagedResult,
    RiskAlertDetail,
    RiskAlertItem,
    RiskRuleItem,
    RiskRuleUpsertRequest,
    RoleInfo,
    SystemConfigItem,
    SystemConfigUpdateRequest,
    WorkorderActionItem,
    WorkorderDetail,
    WorkorderItem,
    WorkorderTransitionRequest,
)
from app.schemas.user import UserProfile
from app.services.db_init import ROLE_DETAILS


def _paginate[T](items: list[T], page: int, page_size: int) -> PagedResult:
    start = (page - 1) * page_size
    end = start + page_size
    return PagedResult(
        items=items[start:end],
        pagination=PaginationMeta(page=page, page_size=page_size, total=len(items)),
    )


def _to_str(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return value


def _parse_notes(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    result: dict[str, str] = {}
    for pair in raw.split(";"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        result[key] = value
    return result


def _dump_notes(values: dict[str, str]) -> str:
    return ";".join(f"{key}={value}" for key, value in values.items())


def get_paged_payload(items: list, page: int, page_size: int) -> PagedResult:
    return _paginate(items, page, page_size)


def list_roles() -> list[RoleInfo]:
    with session_scope() as session:
        rows = session.execute(
            select(UserRoleLink.role_id, func.count(UserRoleLink.user_id)).group_by(UserRoleLink.role_id)
        ).all()
        counts = {role_id: count for role_id, count in rows}

        role_rows = session.execute(select(UserRoleLink).options(selectinload(UserRoleLink.role))).scalars().all()
        role_id_to_code = {link.role_id: UserRole(link.role.code) for link in role_rows}
        role_counts = {role: 0 for role in ROLE_DETAILS}
        for role_id, count in counts.items():
            role = role_id_to_code.get(role_id)
            if role:
                role_counts[role] = count

        return [
            RoleInfo(
                code=role,
                name=str(detail["name"]),
                description=str(detail["description"]),
                permissions=[str(item) for item in detail["permissions"]],
                user_count=role_counts.get(role, 0),
            )
            for role, detail in ROLE_DETAILS.items()
        ]


def list_admin_users(keyword: str | None = None, role: UserRole | None = None) -> list[AdminUserItem]:
    with session_scope() as session:
        query = select(User).options(selectinload(User.roles).selectinload(UserRoleLink.role))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(or_(User.username.ilike(pattern), User.display_name.ilike(pattern)))
        users = session.execute(query.order_by(User.created_at.asc())).scalars().all()

        result: list[AdminUserItem] = []
        for user in users:
            roles = [UserRole(link.role.code) for link in user.roles]
            if role and role not in roles:
                continue
            permissions: list[str] = []
            for role_item in roles:
                permissions.extend(str(item) for item in ROLE_DETAILS[role_item]["permissions"])
            result.append(
                AdminUserItem(
                    user_id=user.id,
                    username=user.username,
                    display_name=user.display_name,
                    phone=user.phone,
                    status=user.status,
                    roles=roles,
                    permissions=list(dict.fromkeys(permissions)),
                    last_login_at=user.last_login_at,
                )
            )
        return result


def list_bindings(user: UserProfile) -> list[BindingItem]:
    ElderUser = aliased(User)
    FamilyUser = aliased(User)
    with session_scope() as session:
        query = (
            select(ElderFamilyBinding, ElderUser.display_name, FamilyUser.display_name)
            .join(ElderUser, ElderFamilyBinding.elder_user_id == ElderUser.id)
            .join(FamilyUser, ElderFamilyBinding.family_user_id == FamilyUser.id)
        )
        if UserRole.FAMILY in user.roles:
            query = query.where(ElderFamilyBinding.family_user_id == user.user_id)
        elif UserRole.ELDER in user.roles:
            query = query.where(ElderFamilyBinding.elder_user_id == user.user_id)

        rows = session.execute(query.order_by(ElderFamilyBinding.created_at.desc())).all()
        return [
            BindingItem(
                id=binding.id,
                elder_user_id=binding.elder_user_id,
                elder_name=elder_name,
                family_user_id=binding.family_user_id,
                family_name=family_name,
                relationship_type=binding.relationship_type,
                status=binding.status,
                is_emergency_contact=binding.is_emergency_contact,
                authorized_at=binding.authorized_at or "",
            )
            for binding, elder_name, family_name in rows
        ]


def create_binding(payload: BindingCreateRequest) -> BindingItem:
    with session_scope() as session:
        existing = session.scalar(
            select(ElderFamilyBinding).where(
                ElderFamilyBinding.elder_user_id == payload.elder_user_id,
                ElderFamilyBinding.family_user_id == payload.family_user_id,
            )
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="绑定关系已存在")

        elder = session.get(User, payload.elder_user_id)
        family = session.get(User, payload.family_user_id)
        if not elder or not family:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定用户不存在")

        binding = ElderFamilyBinding(
            elder_user_id=payload.elder_user_id,
            family_user_id=payload.family_user_id,
            relationship_type=payload.relationship_type,
            is_emergency_contact=payload.is_emergency_contact,
            status="active",
            authorized_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
        session.add(binding)
        session.flush()
        return BindingItem(
            id=binding.id,
            elder_user_id=binding.elder_user_id,
            elder_name=elder.display_name,
            family_user_id=binding.family_user_id,
            family_name=family.display_name,
            relationship_type=binding.relationship_type,
            status=binding.status,
            is_emergency_contact=binding.is_emergency_contact,
            authorized_at=binding.authorized_at or "",
        )


def update_binding(binding_id: str, payload: BindingUpdateRequest) -> BindingItem:
    with session_scope() as session:
        binding = session.get(ElderFamilyBinding, binding_id)
        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定关系不存在")
        if payload.relationship_type is not None:
            binding.relationship_type = payload.relationship_type
        if payload.status is not None:
            binding.status = payload.status
        if payload.is_emergency_contact is not None:
            binding.is_emergency_contact = payload.is_emergency_contact
        elder = session.get(User, binding.elder_user_id)
        family = session.get(User, binding.family_user_id)
        return BindingItem(
            id=binding.id,
            elder_user_id=binding.elder_user_id,
            elder_name=elder.display_name if elder else "",
            family_user_id=binding.family_user_id,
            family_name=family.display_name if family else "",
            relationship_type=binding.relationship_type,
            status=binding.status,
            is_emergency_contact=binding.is_emergency_contact,
            authorized_at=binding.authorized_at or "",
        )


def delete_binding(binding_id: str) -> None:
    with session_scope() as session:
        binding = session.get(ElderFamilyBinding, binding_id)
        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定关系不存在")
        session.delete(binding)


def list_risk_alerts(user: UserProfile, risk_level: str | None = None) -> list[RiskAlertItem]:
    ElderUser = aliased(User)
    with session_scope() as session:
        query = select(RiskAlert, ElderUser.display_name).join(ElderUser, RiskAlert.elder_user_id == ElderUser.id)
        if risk_level:
            query = query.where(RiskAlert.risk_level == risk_level)
        if UserRole.FAMILY in user.roles:
            binding_subquery = select(ElderFamilyBinding.elder_user_id).where(ElderFamilyBinding.family_user_id == user.user_id)
            query = query.where(RiskAlert.elder_user_id.in_(binding_subquery))
        elif UserRole.ELDER in user.roles:
            query = query.where(RiskAlert.elder_user_id == user.user_id)
        rows = session.execute(query.order_by(RiskAlert.occurred_at.desc())).all()
        return [
            RiskAlertItem(
                id=alert.id,
                elder_user_id=alert.elder_user_id,
                elder_name=elder_name,
                source_type=alert.source_type,
                risk_level=alert.risk_level,
                risk_score=alert.risk_score,
                title=alert.title,
                summary=alert.summary,
                status=alert.status,
                occurred_at=alert.occurred_at,
            )
            for alert, elder_name in rows
        ]


def get_risk_alert_detail(alert_id: str) -> RiskAlertDetail:
    ElderUser = aliased(User)
    with session_scope() as session:
        row = session.execute(
            select(RiskAlert, ElderUser.display_name)
            .join(ElderUser, RiskAlert.elder_user_id == ElderUser.id)
            .where(RiskAlert.id == alert_id)
        ).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="风险告警不存在")
        alert, elder_name = row
        notification_ids = session.scalars(
            select(NotificationRecord.id).where(NotificationRecord.alert_id == alert.id)
        ).all()
        workorder_ids = session.scalars(select(Workorder.id).where(Workorder.alert_id == alert.id)).all()
        hit_rule_codes: list[str] = []
        if alert.source_type == "sms" and alert.source_record_id:
            record = session.get(SmsRecognitionRecord, alert.source_record_id)
            if record and record.hit_rule_codes:
                hit_rule_codes = [item for item in record.hit_rule_codes.split(",") if item]
        if alert.source_type == "call" and alert.source_record_id:
            record = session.get(CallRecognitionRecord, alert.source_record_id)
            if record and record.hit_rule_codes:
                hit_rule_codes = [item for item in record.hit_rule_codes.split(",") if item]
        return RiskAlertDetail(
            id=alert.id,
            elder_user_id=alert.elder_user_id,
            elder_name=elder_name,
            source_type=alert.source_type,
            risk_level=alert.risk_level,
            risk_score=alert.risk_score,
            title=alert.title,
            summary=alert.summary,
            status=alert.status,
            occurred_at=alert.occurred_at,
            reason_detail=alert.reason_detail or "",
            suggestion_action=alert.suggestion_action or "",
            hit_rule_codes=hit_rule_codes,
            related_notification_ids=list(notification_ids),
            related_workorder_ids=list(workorder_ids),
        )


def list_notifications(user: UserProfile, is_read: bool | None = None) -> list[NotificationItem]:
    ReceiverUser = aliased(User)
    ElderUser = aliased(User)
    with session_scope() as session:
        query = (
            select(
                NotificationRecord,
                ReceiverUser.display_name,
                RiskAlert.title,
                RiskAlert.risk_level,
                ElderUser.display_name,
            )
            .join(ReceiverUser, NotificationRecord.receiver_user_id == ReceiverUser.id)
            .join(RiskAlert, NotificationRecord.alert_id == RiskAlert.id)
            .join(ElderUser, RiskAlert.elder_user_id == ElderUser.id)
            .where(NotificationRecord.receiver_user_id == user.user_id)
        )
        if is_read is not None:
            query = query.where(NotificationRecord.is_read == is_read)
        rows = session.execute(query.order_by(NotificationRecord.sent_at.desc())).all()
        return [
            NotificationItem(
                id=item.id,
                receiver_user_id=item.receiver_user_id,
                receiver_name=receiver_name,
                alert_id=item.alert_id,
                alert_title=alert_title,
                elder_name=elder_name,
                risk_level=risk_level,
                channel=item.channel,
                notification_type=item.notification_type,
                title=item.title,
                content=item.content,
                status=item.status,
                is_read=item.is_read,
                sent_at=item.sent_at or "",
            )
            for item, receiver_name, alert_title, risk_level, elder_name in rows
        ]


def mark_notification_read(notification_id: str, user: UserProfile) -> NotificationReadResult:
    with session_scope() as session:
        item = session.get(NotificationRecord, notification_id)
        if not item or item.receiver_user_id != user.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
        item.is_read = True
        item.read_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        return NotificationReadResult(id=item.id, is_read=item.is_read, read_at=item.read_at)


def create_help_request(user: UserProfile, payload: HelpRequestCreate) -> HelpRequestResult:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    notification_ids: list[str] = []
    with session_scope() as session:
        current_user = session.get(User, user.user_id)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        latest_alert = session.scalar(
            select(RiskAlert)
            .where(RiskAlert.elder_user_id == user.user_id)
            .order_by(RiskAlert.occurred_at.desc())
        )
        if payload.notify_family:
            family_bindings = session.execute(
                select(ElderFamilyBinding).where(ElderFamilyBinding.elder_user_id == user.user_id)
            ).scalars().all()
            for binding in family_bindings:
                notification = NotificationRecord(
                    alert_id=(latest_alert.id if latest_alert else "alert-001"),
                    receiver_user_id=binding.family_user_id,
                    channel="app",
                    notification_type="help_request",
                    title=f"{current_user.display_name} 发起一键求助",
                    content=payload.note or "老人发起求助，请尽快回电确认。",
                    status="sent",
                    is_read=False,
                    sent_at=now,
                )
                session.add(notification)
                session.flush()
                notification_ids.append(notification.id)
        if payload.notify_community:
            community_users = session.execute(
                select(User)
                .join(User.roles)
                .join(UserRoleLink.role)
                .where(Role.code == UserRole.COMMUNITY.value)
            ).scalars().all()
            for community_user in community_users[:1]:
                notification = NotificationRecord(
                    alert_id=(latest_alert.id if latest_alert else "alert-001"),
                    receiver_user_id=community_user.id,
                    channel="workbench",
                    notification_type="help_request",
                    title=f"{current_user.display_name} 需要协助",
                    content=payload.note or "老人发起求助，请安排回访。",
                    status="sent",
                    is_read=False,
                    sent_at=now,
                )
                session.add(notification)
                session.flush()
                notification_ids.append(notification.id)
        return HelpRequestResult(
            help_id=f"help-{user.user_id}-{int(datetime.now(UTC).timestamp())}",
            action_type=payload.action_type,
            created_at=now,
            notification_ids=notification_ids,
            summary="已向家属/社区发送求助通知并记录留痕。",
        )


def send_family_reminder(user: UserProfile, payload: FamilyReminderCreateRequest) -> FamilyReminderResult:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    with session_scope() as session:
        elder = session.get(User, payload.elder_user_id)
        if not elder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="老人不存在")
        latest_alert = session.scalar(
            select(RiskAlert)
            .where(RiskAlert.elder_user_id == payload.elder_user_id)
            .order_by(RiskAlert.occurred_at.desc())
        )
        notification = NotificationRecord(
            alert_id=(latest_alert.id if latest_alert else "alert-001"),
            receiver_user_id=payload.elder_user_id,
            channel=payload.channel,
            notification_type="family_reminder",
            title=f"{user.display_name} 向您发送了提醒",
            content=payload.content,
            status="sent",
            is_read=False,
            sent_at=now,
        )
        session.add(notification)
        session.flush()
        return FamilyReminderResult(
            notification_id=notification.id,
            sent_at=now,
            receiver_name=elder.display_name,
            content=payload.content,
        )


def get_accessibility_settings(user: UserProfile) -> AccessibilitySettings:
    with session_scope() as session:
        current_user = session.get(User, user.user_id)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        notes = _parse_notes(current_user.notes)
        return AccessibilitySettings(
            font_scale=notes.get("font_scale", "large"),
            high_contrast=notes.get("high_contrast", "false") == "true",
            voice_assistant=notes.get("voice_assistant", "false") == "true",
            voice_speed=notes.get("voice_speed", "normal"),
        )


def update_accessibility_settings(
    user: UserProfile,
    payload: AccessibilitySettingsUpdateRequest,
) -> AccessibilitySettings:
    with session_scope() as session:
        current_user = session.get(User, user.user_id)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        notes = _parse_notes(current_user.notes)
        notes["font_scale"] = payload.font_scale
        notes["high_contrast"] = "true" if payload.high_contrast else "false"
        notes["voice_assistant"] = "true" if payload.voice_assistant else "false"
        notes["voice_speed"] = payload.voice_speed
        current_user.notes = _dump_notes(notes)
        return AccessibilitySettings(
            font_scale=payload.font_scale,
            high_contrast=payload.high_contrast,
            voice_assistant=payload.voice_assistant,
            voice_speed=payload.voice_speed,
        )


def list_community_elders(keyword: str | None = None, risk_level: str | None = None) -> list[CommunityElderItem]:
    with session_scope() as session:
        elder_ids = session.scalars(
            select(ElderFamilyBinding.elder_user_id).distinct()
        ).all()
        elders = session.execute(select(User).where(User.id.in_(elder_ids)).order_by(User.created_at.asc())).scalars().all()
        results: list[CommunityElderItem] = []
        for elder in elders:
            notes = _parse_notes(elder.notes)
            alerts = session.execute(
                select(RiskAlert).where(RiskAlert.elder_user_id == elder.id).order_by(RiskAlert.occurred_at.desc())
            ).scalars().all()
            latest_alert = alerts[0] if alerts else None
            if keyword and keyword not in elder.display_name and keyword not in elder.username:
                continue
            current_risk_level = latest_alert.risk_level if latest_alert else "low"
            if risk_level and current_risk_level != risk_level:
                continue
            results.append(
                CommunityElderItem(
                    elder_user_id=elder.id,
                    elder_name=elder.display_name,
                    age=int(notes.get("age", "0")),
                    gender=notes.get("gender", ""),
                    risk_level=current_risk_level,
                    latest_alert_at=latest_alert.occurred_at if latest_alert else None,
                    latest_alert_title=latest_alert.title if latest_alert else None,
                    tags=[tag for tag in notes.get("tags", "").split("|") if tag],
                    follow_up_status=notes.get("follow_up_status", "pending"),
                    assigned_grid_member=notes.get("assigned_grid_member", ""),
                    alert_count_7d=len(alerts),
                )
            )
        return results


def list_workorders(status_filter: str | None = None) -> list[WorkorderItem]:
    ElderUser = aliased(User)
    AssignedUser = aliased(User)
    with session_scope() as session:
        query = (
            select(Workorder, ElderUser.display_name, AssignedUser.display_name)
            .join(ElderUser, Workorder.elder_user_id == ElderUser.id)
            .outerjoin(AssignedUser, Workorder.assigned_to_user_id == AssignedUser.id)
        )
        if status_filter:
            query = query.where(Workorder.status == status_filter)
        rows = session.execute(query.order_by(Workorder.updated_at.desc())).all()
        return [
            WorkorderItem(
                id=item.id,
                workorder_no=item.workorder_no,
                alert_id=item.alert_id,
                elder_user_id=item.elder_user_id,
                elder_name=elder_name,
                title=item.title,
                priority=item.priority,
                status=item.status,
                assigned_to_user_id=item.assigned_to_user_id,
                assigned_to_name=assigned_name,
                dispose_method=item.dispose_method,
                updated_at=_to_str(item.updated_at) or "",
            )
            for item, elder_name, assigned_name in rows
        ]


def get_workorder_detail(workorder_id: str) -> WorkorderDetail:
    with session_scope() as session:
        workorder = session.scalar(
            select(Workorder)
            .options(selectinload(Workorder.actions).selectinload(WorkorderAction.operator_user))
            .where(Workorder.id == workorder_id)
        )
        if not workorder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
        elder = session.get(User, workorder.elder_user_id)
        assigned = session.get(User, workorder.assigned_to_user_id) if workorder.assigned_to_user_id else None
        alert = session.get(RiskAlert, workorder.alert_id)
        actions = [
            WorkorderActionItem(
                id=item.id,
                action_type=item.action_type,
                operator_user_id=item.operator_user_id or "",
                operator_name=item.operator_user.display_name if item.operator_user else "",
                from_status=item.from_status,
                to_status=item.to_status,
                note=item.note,
                created_at=_to_str(item.created_at) or "",
            )
            for item in sorted(workorder.actions, key=lambda action: action.created_at)
        ]
        return WorkorderDetail(
            id=workorder.id,
            workorder_no=workorder.workorder_no,
            alert_id=workorder.alert_id,
            elder_user_id=workorder.elder_user_id,
            elder_name=elder.display_name if elder else "",
            title=workorder.title,
            priority=workorder.priority,
            status=workorder.status,
            assigned_to_user_id=workorder.assigned_to_user_id,
            assigned_to_name=assigned.display_name if assigned else None,
            dispose_method=workorder.dispose_method,
            updated_at=_to_str(workorder.updated_at) or "",
            dispose_result=workorder.dispose_result,
            closed_at=workorder.closed_at,
            latest_alert_summary=alert.summary if alert else "",
            actions=actions,
        )


def transition_workorder(
    workorder_id: str,
    payload: WorkorderTransitionRequest,
    user: UserProfile,
) -> WorkorderDetail:
    with session_scope() as session:
        workorder = session.get(Workorder, workorder_id)
        if not workorder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
        from_status = workorder.status
        workorder.status = payload.to_status
        workorder.assigned_to_user_id = payload.assigned_to_user_id or workorder.assigned_to_user_id
        workorder.dispose_method = payload.dispose_method or workorder.dispose_method
        workorder.dispose_result = payload.dispose_result or workorder.dispose_result
        if payload.to_status == "closed":
            workorder.closed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        session.add(
            WorkorderAction(
                workorder_id=workorder.id,
                operator_user_id=user.user_id,
                action_type=payload.action_type,
                from_status=from_status,
                to_status=payload.to_status,
                note=payload.note,
            )
        )
        session.flush()
    return get_workorder_detail(workorder_id)


def list_risk_rules() -> list[RiskRuleItem]:
    with session_scope() as session:
        rules = session.execute(select(RiskRule).order_by(RiskRule.priority.asc())).scalars().all()
        return [
            RiskRuleItem(
                id=item.id,
                code=item.code,
                name=item.name,
                scene=item.scene,
                risk_level=item.risk_level,
                priority=item.priority,
                status=item.status,
                trigger_expression=item.trigger_expression,
                reason_template=item.reason_template or "",
                suggestion_template=item.suggestion_template or "",
            )
            for item in rules
        ]


def create_risk_rule(payload: RiskRuleUpsertRequest) -> RiskRuleItem:
    with session_scope() as session:
        item = RiskRule(**payload.model_dump())
        session.add(item)
        session.flush()
        return RiskRuleItem(
            id=item.id,
            code=item.code,
            name=item.name,
            scene=item.scene,
            risk_level=item.risk_level,
            priority=item.priority,
            status=item.status,
            trigger_expression=item.trigger_expression,
            reason_template=item.reason_template or "",
            suggestion_template=item.suggestion_template or "",
        )


def update_risk_rule(rule_id: str, payload: RiskRuleUpsertRequest) -> RiskRuleItem:
    with session_scope() as session:
        item = session.get(RiskRule, rule_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="规则不存在")
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        return RiskRuleItem(
            id=item.id,
            code=item.code,
            name=item.name,
            scene=item.scene,
            risk_level=item.risk_level,
            priority=item.priority,
            status=item.status,
            trigger_expression=item.trigger_expression,
            reason_template=item.reason_template or "",
            suggestion_template=item.suggestion_template or "",
        )


def list_contents() -> list[ContentItem]:
    with session_scope() as session:
        templates = session.execute(select(PromptTemplate)).scalars().all()
        educations = session.execute(select(EducationContent)).scalars().all()
        contents = [
            ContentItem(
                id=item.id,
                content_type="template",
                code=item.code,
                title=item.name,
                category=item.category,
                audience=None,
                channel=item.channel,
                status=item.status,
                summary=item.notes,
                updated_at=_to_str(item.updated_at) or "",
            )
            for item in templates
        ]
        contents.extend(
            ContentItem(
                id=item.id,
                content_type="education",
                code=None,
                title=item.title,
                category=item.category,
                audience=item.audience,
                channel="article",
                status=item.publish_status,
                summary=item.summary,
                updated_at=_to_str(item.updated_at) or "",
            )
            for item in educations
        )
        return sorted(contents, key=lambda item: item.updated_at, reverse=True)


def list_education_contents(
    audience: str | None = None,
    category: str | None = None,
    publish_status: str | None = "published",
) -> list[EducationContentItem]:
    with session_scope() as session:
        query = select(EducationContent)
        if audience:
            query = query.where(EducationContent.audience == audience)
        if category:
            query = query.where(EducationContent.category == category)
        if publish_status:
            query = query.where(EducationContent.publish_status == publish_status)
        rows = session.execute(query.order_by(EducationContent.updated_at.desc())).scalars().all()
        return [
            EducationContentItem(
                id=item.id,
                title=item.title,
                category=item.category,
                audience=item.audience,
                summary=item.summary,
                content_body=item.content_body,
                publish_status=item.publish_status,
                published_at=item.published_at,
            )
            for item in rows
        ]


def create_content(payload: ContentUpsertRequest) -> ContentItem:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    with session_scope() as session:
        if payload.content_type == "template":
            item = PromptTemplate(
                code=payload.code or f"TPL-{int(datetime.now(UTC).timestamp())}",
                name=payload.title,
                category=payload.category,
                channel=payload.channel or "app",
                content=payload.content_body,
                status=payload.status,
                notes=payload.summary,
            )
            session.add(item)
            session.flush()
            return ContentItem(
                id=item.id,
                content_type="template",
                code=item.code,
                title=item.name,
                category=item.category,
                audience=None,
                channel=item.channel,
                status=item.status,
                summary=item.notes,
                updated_at=now,
            )
        item = EducationContent(
            title=payload.title,
            category=payload.category,
            audience=payload.audience or "elder",
            summary=payload.summary,
            content_body=payload.content_body,
            publish_status=payload.status,
            published_at=now if payload.status == "published" else None,
        )
        session.add(item)
        session.flush()
        return ContentItem(
            id=item.id,
            content_type="education",
            code=None,
            title=item.title,
            category=item.category,
            audience=item.audience,
            channel="article",
            status=item.publish_status,
            summary=item.summary,
            updated_at=now,
        )


def update_content(content_id: str, payload: ContentUpsertRequest) -> ContentItem:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    with session_scope() as session:
        if payload.content_type == "template":
            item = session.get(PromptTemplate, content_id)
            if not item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")
            item.code = payload.code or item.code
            item.name = payload.title
            item.category = payload.category
            item.channel = payload.channel or item.channel
            item.content = payload.content_body
            item.status = payload.status
            item.notes = payload.summary
            return ContentItem(
                id=item.id,
                content_type="template",
                code=item.code,
                title=item.name,
                category=item.category,
                audience=None,
                channel=item.channel,
                status=item.status,
                summary=item.notes,
                updated_at=now,
            )
        item = session.get(EducationContent, content_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")
        item.title = payload.title
        item.category = payload.category
        item.audience = payload.audience or item.audience
        item.summary = payload.summary
        item.content_body = payload.content_body
        item.publish_status = payload.status
        item.published_at = now if payload.status == "published" else item.published_at
        return ContentItem(
            id=item.id,
            content_type="education",
            code=None,
            title=item.title,
            category=item.category,
            audience=item.audience,
            channel="article",
            status=item.publish_status,
            summary=item.summary,
            updated_at=now,
        )


def list_system_configs() -> list[SystemConfigItem]:
    with session_scope() as session:
        rows = session.execute(select(SystemConfig).order_by(SystemConfig.group.asc(), SystemConfig.key.asc())).scalars().all()
        return [
            SystemConfigItem(
                key=item.key,
                name=item.name,
                value=item.value,
                group=item.group,
                description=item.description or "",
            )
            for item in rows
        ]


def update_system_config(config_key: str, payload: SystemConfigUpdateRequest) -> SystemConfigItem:
    with session_scope() as session:
        item = session.scalar(select(SystemConfig).where(SystemConfig.key == config_key))
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
        item.value = payload.value
        return SystemConfigItem(
            key=item.key,
            name=item.name,
            value=item.value,
            group=item.group,
            description=item.description or "",
        )


def get_community_report() -> CommunityReportData:
    with session_scope() as session:
        alerts = session.execute(select(RiskAlert)).scalars().all()
        workorders = session.execute(select(Workorder)).scalars().all()
        educations = session.execute(select(EducationContent)).scalars().all()
        risk_by_level = [
            {"label": level, "count": len([item for item in alerts if item.risk_level == level])}
            for level in ["high", "medium", "low"]
        ]
        workorder_status = [
            {"label": status_name, "count": len([item for item in workorders if item.status == status_name])}
            for status_name in ["pending", "processing", "closed"]
        ]
        education_summary = [
            {"label": status_name, "count": len([item for item in educations if item.publish_status == status_name])}
            for status_name in ["published", "draft"]
        ]
        closed_workorders = [item for item in workorders if item.closed_at]
        avg_minutes = 0
        if closed_workorders:
            total_minutes = 0
            for item in closed_workorders:
                created = item.created_at
                closed = datetime.fromisoformat(item.closed_at.replace("Z", "+00:00"))
                total_minutes += int((closed - created).total_seconds() / 60)
            avg_minutes = int(total_minutes / len(closed_workorders))
        return CommunityReportData(
            risk_by_level=risk_by_level,
            workorder_status=workorder_status,
            education_summary=education_summary,
            disposal_avg_minutes=avg_minutes,
        )
