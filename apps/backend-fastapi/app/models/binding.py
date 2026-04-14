from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ElderFamilyBinding(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "elder_family_bindings"
    __table_args__ = (
        UniqueConstraint("elder_user_id", "family_user_id", name="uq_elder_family_bindings_pair"),
    )

    elder_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    family_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    is_emergency_contact: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    authorized_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    revoked_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    elder_user: Mapped["User"] = relationship(foreign_keys=[elder_user_id], back_populates="elder_bindings")
    family_user: Mapped["User"] = relationship(foreign_keys=[family_user_id], back_populates="family_bindings")


if TYPE_CHECKING:
    from app.models.user import User
