from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Workorder(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "workorders"

    alert_id: Mapped[str] = mapped_column(ForeignKey("risk_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    elder_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_to_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    workorder_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", server_default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    dispose_method: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dispose_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    alert: Mapped["RiskAlert"] = relationship(back_populates="workorders")
    elder_user: Mapped["User"] = relationship(foreign_keys=[elder_user_id])
    assigned_to_user: Mapped["User | None"] = relationship(foreign_keys=[assigned_to_user_id])
    actions: Mapped[list["WorkorderAction"]] = relationship(back_populates="workorder", cascade="all, delete-orphan")


class WorkorderAction(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "workorder_actions"

    workorder_id: Mapped[str] = mapped_column(ForeignKey("workorders.id", ondelete="CASCADE"), nullable=False, index=True)
    operator_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    workorder: Mapped["Workorder"] = relationship(back_populates="actions")
    operator_user: Mapped["User | None"] = relationship()


if TYPE_CHECKING:
    from app.models.risk import RiskAlert
    from app.models.user import User
