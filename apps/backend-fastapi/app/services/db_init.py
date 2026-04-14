from __future__ import annotations

from sqlalchemy import select

from app.constants.roles import UserRole
from app.db.base import Base
from app.db.session import get_engine, session_scope
from app.models import (
    EducationContent,
    ElderFamilyBinding,
    NotificationRecord,
    PromptTemplate,
    RiskAlert,
    RiskLexiconTerm,
    RiskRule,
    Role,
    SmsRecognitionRecord,
    SystemConfig,
    User,
    UserRoleLink,
    Workorder,
    WorkorderAction,
)

ROLE_DETAILS: dict[UserRole, dict[str, str | list[str]]] = {
    UserRole.ELDER: {
        "name": "老年用户",
        "description": "接收风险提醒、求助和亲属绑定。",
        "permissions": ["elder:read", "sos:create", "binding:manage"],
    },
    UserRole.FAMILY: {
        "name": "子女用户",
        "description": "查看老人风险、接收通知和监护设置。",
        "permissions": ["family:read", "alerts:read", "notifications:read", "bindings:read"],
    },
    UserRole.COMMUNITY: {
        "name": "社区工作人员",
        "description": "查看重点老人、处理工单和回访协同。",
        "permissions": ["community:read", "workorder:read", "workorder:update", "elder-focus:read"],
    },
    UserRole.ADMIN: {
        "name": "系统管理员",
        "description": "管理用户、角色、规则、内容和系统配置。",
        "permissions": ["*"],
    },
}

SEED_USERS = [
    {
        "id": "u-elder-001",
        "username": "elder_demo",
        "password_hash": "Elder123!",
        "display_name": "李阿姨",
        "phone": "13800001001",
        "status": "active",
        "last_login_at": "2026-04-14T08:30:00Z",
        "notes": "age=72;gender=女;tags=高风险|需回访|独居;follow_up_status=pending_visit;assigned_grid_member=社区网格员张强",
        "roles": [UserRole.ELDER],
    },
    {
        "id": "u-elder-002",
        "username": "elder_demo_2",
        "password_hash": "Elder123!",
        "display_name": "周叔叔",
        "phone": "13800001002",
        "status": "active",
        "last_login_at": "2026-04-13T17:20:00Z",
        "notes": "age=68;gender=男;tags=电话回访中;follow_up_status=phone_following;assigned_grid_member=社区社工陈敏",
        "roles": [UserRole.ELDER],
    },
    {
        "id": "u-family-001",
        "username": "family_demo",
        "password_hash": "Family123!",
        "display_name": "王女士",
        "phone": "13900002001",
        "status": "active",
        "last_login_at": "2026-04-14T09:00:00Z",
        "roles": [UserRole.FAMILY],
    },
    {
        "id": "u-family-002",
        "username": "family_demo_2",
        "password_hash": "Family123!",
        "display_name": "李先生",
        "phone": "13900002002",
        "status": "active",
        "last_login_at": "2026-04-13T19:45:00Z",
        "roles": [UserRole.FAMILY],
    },
    {
        "id": "u-community-001",
        "username": "community_demo",
        "password_hash": "Community123!",
        "display_name": "社区网格员张强",
        "phone": "13700003001",
        "status": "active",
        "last_login_at": "2026-04-14T07:50:00Z",
        "roles": [UserRole.COMMUNITY],
    },
    {
        "id": "u-community-002",
        "username": "community_demo_2",
        "password_hash": "Community123!",
        "display_name": "社区社工陈敏",
        "phone": "13700003002",
        "status": "active",
        "last_login_at": "2026-04-13T18:10:00Z",
        "roles": [UserRole.COMMUNITY],
    },
    {
        "id": "u-admin-001",
        "username": "admin_demo",
        "password_hash": "Admin123!",
        "display_name": "系统管理员",
        "phone": "13600004001",
        "status": "active",
        "last_login_at": "2026-04-14T08:10:00Z",
        "roles": [UserRole.ADMIN],
    },
]


def ensure_database_ready() -> None:
    Base.metadata.create_all(bind=get_engine())
    with session_scope() as session:
        existing_user = session.scalar(select(User.id).limit(1))
        if existing_user:
            return

        role_rows: dict[UserRole, Role] = {}
        for role_code, detail in ROLE_DETAILS.items():
            role = Role(
                id=f"role-{role_code.value}",
                code=role_code.value,
                name=str(detail["name"]),
                description=str(detail["description"]),
                is_system=True,
            )
            role_rows[role_code] = role
            session.add(role)

        for item in SEED_USERS:
            payload = {key: value for key, value in item.items() if key != "roles"}
            roles = list(item["roles"])
            user = User(**payload)
            session.add(user)
            session.flush()
            for role in roles:
                session.add(
                    UserRoleLink(
                        id=f"url-{user.id}-{role.value}",
                        user_id=user.id,
                        role_id=role_rows[role].id,
                    )
                )

        session.add_all(
            [
                ElderFamilyBinding(
                    id="bind-001",
                    elder_user_id="u-elder-001",
                    family_user_id="u-family-001",
                    relationship_type="daughter",
                    status="active",
                    is_emergency_contact=True,
                    authorized_at="2026-04-10T10:00:00Z",
                ),
                ElderFamilyBinding(
                    id="bind-002",
                    elder_user_id="u-elder-002",
                    family_user_id="u-family-002",
                    relationship_type="son",
                    status="active",
                    is_emergency_contact=True,
                    authorized_at="2026-04-09T15:20:00Z",
                ),
                SmsRecognitionRecord(
                    id="sms-001",
                    elder_user_id="u-elder-001",
                    sender="95533",
                    message_text="您有一笔退款待领取，请点击短链并提供验证码完成补偿。",
                    masked_message_text="您有一笔退款待领取，请点击短链并提供验证码完成补偿。",
                    risk_level="high",
                    risk_score=92,
                    hit_rule_codes="SMS_REFUND_LINK,SMS_VERIFY_CODE",
                    hit_terms="退款链接,验证码,客服补偿",
                    analysis_summary="命中短信退款链接与验证码索取规则，存在高风险诈骗特征。",
                    suggestion_action="不要点击链接，不要透露验证码，建议联系子女核实并保留短信截图。",
                    occurred_at="2026-04-14T08:22:00Z",
                ),
                RiskAlert(
                    id="alert-001",
                    elder_user_id="u-elder-001",
                    source_type="sms",
                    source_record_id="sms-001",
                    risk_level="high",
                    risk_score=92,
                    title="疑似冒充客服退款短信",
                    summary="短信包含退款链接与验证码索取内容，存在诱导转账风险。",
                    reason_detail="命中“退款链接”“验证码”“客服补偿”多条高危规则，且短信中包含短链。",
                    suggestion_action="不要点击链接，不要透露验证码，建议联系子女核实并保留短信截图。",
                    status="pending_follow_up",
                    occurred_at="2026-04-14T08:22:00Z",
                ),
                RiskAlert(
                    id="alert-002",
                    elder_user_id="u-elder-002",
                    source_type="call",
                    source_record_id=None,
                    risk_level="medium",
                    risk_score=71,
                    title="疑似冒充公检法来电",
                    summary="通话中出现“安全账户”“配合调查”等敏感话术。",
                    reason_detail="命中公检法冒充与转账诱导话术，语义强度中等。",
                    suggestion_action="先挂断电话，通过官方渠道回拨核实，不要转账。",
                    status="new",
                    occurred_at="2026-04-13T19:10:00Z",
                ),
                NotificationRecord(
                    id="notify-001",
                    receiver_user_id="u-family-001",
                    alert_id="alert-001",
                    channel="app",
                    notification_type="risk_alert",
                    title="老人收到高风险诈骗短信",
                    content="李阿姨于 08:22 收到疑似退款诈骗短信，请尽快联系提醒。",
                    status="sent",
                    is_read=False,
                    sent_at="2026-04-14T08:23:00Z",
                ),
                NotificationRecord(
                    id="notify-002",
                    receiver_user_id="u-community-001",
                    alert_id="alert-001",
                    channel="workbench",
                    notification_type="community_dispatch",
                    title="辖区出现高风险老人告警",
                    content="李阿姨命中高风险诈骗规则，建议安排电话回访。",
                    status="sent",
                    is_read=True,
                    sent_at="2026-04-14T08:25:00Z",
                ),
                NotificationRecord(
                    id="notify-003",
                    receiver_user_id="u-family-002",
                    alert_id="alert-002",
                    channel="sms",
                    notification_type="risk_alert",
                    title="老人疑似接到冒充公检法电话",
                    content="周叔叔昨日晚间接到疑似诈骗电话，建议尽快回访。",
                    status="sent",
                    is_read=False,
                    sent_at="2026-04-13T19:15:00Z",
                ),
                Workorder(
                    id="wo-001",
                    workorder_no="GD202604140001",
                    alert_id="alert-001",
                    elder_user_id="u-elder-001",
                    title="李阿姨高风险短信回访工单",
                    priority="high",
                    status="processing",
                    assigned_to_user_id="u-community-001",
                    dispose_method="phone_visit",
                    dispose_result=None,
                    closed_at=None,
                ),
                WorkorderAction(
                    id="woa-001",
                    workorder_id="wo-001",
                    operator_user_id="u-admin-001",
                    action_type="create",
                    from_status=None,
                    to_status="pending",
                    note="高风险短信自动转工单。",
                ),
                WorkorderAction(
                    id="woa-002",
                    workorder_id="wo-001",
                    operator_user_id="u-admin-001",
                    action_type="assign",
                    from_status="pending",
                    to_status="processing",
                    note="已指派社区网格员张强电话回访。",
                ),
                RiskRule(
                    id="rule-001",
                    code="SMS_REFUND_LINK",
                    name="短信退款链接识别",
                    scene="sms",
                    risk_level="high",
                    priority=10,
                    status="enabled",
                    trigger_expression="contains(refund) && contains(short_link)",
                    reason_template="短信涉及退款链接与身份核验，疑似引导跳转诈骗页面。",
                    suggestion_template="不要点击链接，建议联系官方客服核实。",
                ),
                RiskRule(
                    id="rule-002",
                    code="CALL_POLICE_IMPERSONATION",
                    name="冒充公检法来电",
                    scene="call",
                    risk_level="medium",
                    priority=20,
                    status="enabled",
                    trigger_expression="contains(security_account) && contains(investigation)",
                    reason_template="来电出现安全账户与配合调查话术。",
                    suggestion_template="挂断后主动拨打官方电话核实。",
                ),
                RiskLexiconTerm(
                    id="lex-001",
                    term="验证码",
                    category="sms_keyword",
                    scene="sms",
                    risk_level="high",
                    status="enabled",
                    source="seed",
                    notes="短信验证码索取高危词",
                ),
                PromptTemplate(
                    id="content-001",
                    code="ALERT_HIGH_RISK_FAMILY",
                    name="高风险通知模板",
                    category="notification_template",
                    channel="app",
                    content="老人收到高风险诈骗信息，请尽快联系核实。",
                    status="enabled",
                    is_default=True,
                    notes="用于子女端高风险告警提醒。",
                ),
                EducationContent(
                    id="content-002",
                    title="警惕冒充客服退款骗局",
                    category="anti_fraud_article",
                    audience="elder",
                    summary="讲解常见退款诈骗套路与识别要点。",
                    content_body="常见退款诈骗会伪装客服，诱导点击链接并索取验证码。",
                    publish_status="published",
                    published_at="2026-04-13T16:00:00Z",
                ),
                SystemConfig(
                    id="cfg-001",
                    key="risk.high_threshold",
                    name="高风险分数阈值",
                    value="85",
                    group="risk",
                    description="达到该分值时自动通知子女并生成社区工单。",
                ),
                SystemConfig(
                    id="cfg-002",
                    key="notification.family_channels",
                    name="子女通知渠道",
                    value="app,sms",
                    group="notification",
                    description="高风险事件默认通知渠道。",
                ),
                SystemConfig(
                    id="cfg-003",
                    key="workorder.auto_dispatch",
                    name="自动派单开关",
                    value="true",
                    group="workorder",
                    description="高风险告警是否自动生成社区工单。",
                ),
            ]
        )
