from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RiskAlert(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "risk_alerts"

    elder_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source_record_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new", server_default="new")
    occurred_at: Mapped[str] = mapped_column(String(40), nullable=False)

    elder_user: Mapped["User"] = relationship()
    notifications: Mapped[list["NotificationRecord"]] = relationship(back_populates="alert")
    workorders: Mapped[list["Workorder"]] = relationship(back_populates="alert")


class SmsRecognitionRecord(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "sms_recognition_records"

    elder_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    masked_message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    hit_rule_codes: Mapped[str | None] = mapped_column(Text, nullable=True)
    hit_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[str] = mapped_column(String(40), nullable=False)

    elder_user: Mapped["User"] = relationship()


class CallRecognitionRecord(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "call_recognition_records"

    elder_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    caller_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    hit_rule_codes: Mapped[str | None] = mapped_column(Text, nullable=True)
    hit_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[str] = mapped_column(String(40), nullable=False)

    elder_user: Mapped["User"] = relationship()


if TYPE_CHECKING:
    from app.models.notification import NotificationRecord
    from app.models.user import User
    from app.models.workorder import Workorder
