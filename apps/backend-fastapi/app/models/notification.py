from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class NotificationRecord(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "notification_records"

    alert_id: Mapped[str] = mapped_column(ForeignKey("risk_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    notification_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    read_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    sent_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    alert: Mapped["RiskAlert"] = relationship(back_populates="notifications")
    receiver_user: Mapped["User"] = relationship()


if TYPE_CHECKING:
    from app.models.risk import RiskAlert
    from app.models.user import User
