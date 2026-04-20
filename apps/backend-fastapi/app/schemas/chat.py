from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatUserSearchItem(BaseModel):
    user_id: str
    username: str
    display_name: str
    phone: str
    status: str


class CreateConversationRequest(BaseModel):
    conversation_type: Literal["direct"] = "direct"
    participant_user_ids: list[str] = Field(min_length=1, max_length=1)
    title: str | None = Field(default=None, max_length=100)


class ChatConversationItem(BaseModel):
    id: str
    conversation_type: str
    title: str
    peer_user_id: str | None = None
    peer_name: str | None = None
    peer_status: str | None = None
    unread_count: int
    last_message_preview: str | None = None
    last_message_at: str | None = None
    last_message_id: str | None = None


class ChatConversationMemberItem(BaseModel):
    user_id: str
    display_name: str
    status: str
    joined_at: str | None = None
    last_read_message_id: str | None = None
    last_read_at: str | None = None
    unread_count: int


class ChatSendMessageRequest(BaseModel):
    message_type: Literal["text", "image", "audio", "video", "file", "card"] = "text"
    content_text: str = Field(min_length=1, max_length=5000)
    content_json: dict[str, Any] | None = None


class ChatMessageItem(BaseModel):
    id: str
    conversation_id: str
    sender_user_id: str
    sender_name: str
    message_type: str
    content_text: str
    content_json: dict[str, Any] | None = None
    status: str
    is_self: bool
    delivered_at: str | None = None
    read_by_all_at: str | None = None
    risk_level: str
    risk_category: str | None = None
    risk_reason: str | None = None
    risk_suggestion: str | None = None
    created_at: str


class ChatConversationDetail(ChatConversationItem):
    members: list[ChatConversationMemberItem]
    messages: list[ChatMessageItem]
    pagination: dict[str, int]


class MarkMessageReadRequest(BaseModel):
    last_read_message_id: str


class ChatUnreadSummary(BaseModel):
    total_unread: int


class OnlineStateItem(BaseModel):
    user_id: str
    is_online: bool
    last_seen_at: str | None = None
    client_type: str | None = None
