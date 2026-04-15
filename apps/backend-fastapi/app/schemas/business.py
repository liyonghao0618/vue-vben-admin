from typing import Any

from pydantic import BaseModel, Field

from app.constants.roles import UserRole


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = Field(default=None, description="Reserved for future use")


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutResponse(BaseModel):
    success: bool = True


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class PagedResult(BaseModel):
    items: list[Any]
    pagination: PaginationMeta


class RoleInfo(BaseModel):
    code: UserRole
    name: str
    description: str
    permissions: list[str]
    user_count: int | None = None


class BindingItem(BaseModel):
    id: str
    elder_user_id: str
    elder_name: str
    family_user_id: str
    family_name: str
    relationship_type: str
    status: str
    is_emergency_contact: bool
    authorized_at: str


class BindingCreateRequest(BaseModel):
    elder_user_id: str
    family_user_id: str
    relationship_type: str = Field(min_length=1, max_length=30)
    is_emergency_contact: bool = False


class BindingUpdateRequest(BaseModel):
    relationship_type: str | None = Field(default=None, min_length=1, max_length=30)
    status: str | None = None
    is_emergency_contact: bool | None = None


class RiskAlertItem(BaseModel):
    id: str
    elder_user_id: str
    elder_name: str
    source_type: str
    risk_level: str
    risk_score: int
    title: str
    summary: str
    status: str
    occurred_at: str


class RiskAlertDetail(RiskAlertItem):
    reason_detail: str
    suggestion_action: str
    hit_rule_codes: list[str]
    related_notification_ids: list[str]
    related_workorder_ids: list[str]


class SmsRecognitionRequest(BaseModel):
    elder_user_id: str
    sender: str | None = None
    message_text: str = Field(min_length=1, max_length=5000)
    occurred_at: str | None = None


class CallRecognitionRequest(BaseModel):
    elder_user_id: str
    caller_number: str | None = None
    transcript_text: str = Field(min_length=1, max_length=10000)
    duration_seconds: int | None = Field(default=None, ge=0)
    occurred_at: str | None = None


class RiskRecognitionResult(BaseModel):
    scene: str
    record_id: str
    risk_level: str
    risk_score: int
    hit_rule_codes: list[str]
    hit_terms: list[str]
    reason_detail: str
    suggestion_action: str
    alert_id: str | None
    notification_ids: list[str]
    workorder_id: str | None


class NotificationItem(BaseModel):
    id: str
    receiver_user_id: str
    receiver_name: str
    alert_id: str
    alert_title: str
    elder_name: str
    risk_level: str
    channel: str
    notification_type: str
    title: str
    content: str
    status: str
    is_read: bool
    sent_at: str


class NotificationReadResult(BaseModel):
    id: str
    is_read: bool
    read_at: str | None


class HelpRequestCreate(BaseModel):
    action_type: str = Field(min_length=1, max_length=30)
    note: str | None = Field(default=None, max_length=500)
    notify_family: bool = True
    notify_community: bool = True


class HelpRequestResult(BaseModel):
    help_id: str
    action_type: str
    created_at: str
    notification_ids: list[str]
    summary: str


class FamilyReminderCreateRequest(BaseModel):
    elder_user_id: str
    content: str = Field(min_length=1, max_length=500)
    channel: str = Field(default="app", min_length=1, max_length=20)


class FamilyReminderResult(BaseModel):
    notification_id: str
    sent_at: str
    receiver_name: str
    content: str


class AccessibilitySettings(BaseModel):
    font_scale: str
    high_contrast: bool
    voice_assistant: bool
    voice_speed: str


class AccessibilitySettingsUpdateRequest(BaseModel):
    font_scale: str = Field(min_length=1, max_length=20)
    high_contrast: bool
    voice_assistant: bool
    voice_speed: str = Field(min_length=1, max_length=20)


class CommunityElderItem(BaseModel):
    elder_user_id: str
    elder_name: str
    age: int
    gender: str
    risk_level: str
    latest_alert_at: str | None
    latest_alert_title: str | None
    tags: list[str]
    follow_up_status: str
    assigned_grid_member: str
    alert_count_7d: int


class WorkorderActionItem(BaseModel):
    id: str
    action_type: str
    operator_user_id: str
    operator_name: str
    from_status: str | None
    to_status: str | None
    note: str | None
    created_at: str


class WorkorderItem(BaseModel):
    id: str
    workorder_no: str
    alert_id: str
    elder_user_id: str
    elder_name: str
    title: str
    priority: str
    status: str
    assigned_to_user_id: str | None
    assigned_to_name: str | None
    dispose_method: str | None
    updated_at: str


class WorkorderDetail(WorkorderItem):
    dispose_result: str | None
    closed_at: str | None
    latest_alert_summary: str
    actions: list[WorkorderActionItem]


class WorkorderTransitionRequest(BaseModel):
    action_type: str = Field(min_length=1, max_length=30)
    to_status: str = Field(min_length=1, max_length=20)
    note: str | None = Field(default=None, max_length=500)
    assigned_to_user_id: str | None = None
    dispose_method: str | None = Field(default=None, max_length=30)
    dispose_result: str | None = Field(default=None, max_length=1000)


class AdminUserItem(BaseModel):
    user_id: str
    username: str
    display_name: str
    phone: str
    status: str
    roles: list[UserRole]
    permissions: list[str]
    last_login_at: str | None


class RiskRuleItem(BaseModel):
    id: str
    code: str
    name: str
    scene: str
    risk_level: str
    priority: int
    status: str
    trigger_expression: str
    reason_template: str
    suggestion_template: str


class RiskRuleUpsertRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    scene: str = Field(min_length=1, max_length=20)
    risk_level: str = Field(min_length=1, max_length=20)
    priority: int = Field(default=100, ge=1, le=999)
    status: str = Field(default="enabled", min_length=1, max_length=20)
    trigger_expression: str = Field(min_length=1, max_length=2000)
    reason_template: str = Field(default="", max_length=2000)
    suggestion_template: str = Field(default="", max_length=2000)


class ContentItem(BaseModel):
    id: str
    content_type: str
    code: str | None = None
    title: str
    category: str
    audience: str | None = None
    channel: str | None = None
    status: str
    summary: str | None = None
    updated_at: str


class ContentUpsertRequest(BaseModel):
    content_type: str = Field(min_length=1, max_length=30)
    code: str | None = Field(default=None, max_length=50)
    title: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=30)
    audience: str | None = Field(default=None, max_length=30)
    channel: str | None = Field(default=None, max_length=20)
    status: str = Field(default="draft", min_length=1, max_length=20)
    summary: str | None = Field(default=None, max_length=255)
    content_body: str = Field(min_length=1, max_length=5000)


class SystemConfigItem(BaseModel):
    key: str
    name: str
    value: str
    group: str
    description: str


class SystemConfigUpdateRequest(BaseModel):
    value: str = Field(min_length=1, max_length=2000)


class EducationContentItem(BaseModel):
    id: str
    title: str
    category: str
    audience: str
    summary: str | None
    content_body: str
    publish_status: str
    published_at: str | None


class CommunityReportData(BaseModel):
    risk_by_level: list[dict[str, int | str]]
    workorder_status: list[dict[str, int | str]]
    education_summary: list[dict[str, int | str]]
    disposal_avg_minutes: int
