from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ChatConversation(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_conversations"

    conversation_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="direct", server_default="direct"
    )
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    last_message_preview: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_message_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    members: Mapped[list["ChatConversationMember"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class ChatConversationMember(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_conversation_members"
    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "user_id",
            name="uq_chat_conversation_members_conversation_user",
        ),
    )

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    joined_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    last_read_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    last_read_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    unread_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_muted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    conversation: Mapped["ChatConversation"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class ChatMessage(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text", server_default="text")
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="sent", server_default="sent")
    delivered_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    read_by_all_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low", server_default="low")
    risk_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)

    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()


class ChatInstancePresence(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "chat_instance_presence"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    connection_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="online", server_default="online")
    last_seen_at: Mapped[str] = mapped_column(String(40), nullable=False)
    client_type: Mapped[str] = mapped_column(String(20), nullable=False, default="web", server_default="web")

    user: Mapped["User"] = relationship()


if TYPE_CHECKING:
    from app.models.user import User
