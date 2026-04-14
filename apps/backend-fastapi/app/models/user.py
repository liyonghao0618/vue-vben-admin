from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    last_login_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    roles: Mapped[list["UserRoleLink"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    elder_bindings: Mapped[list["ElderFamilyBinding"]] = relationship(
        foreign_keys="ElderFamilyBinding.elder_user_id",
        back_populates="elder_user",
    )
    family_bindings: Mapped[list["ElderFamilyBinding"]] = relationship(
        foreign_keys="ElderFamilyBinding.family_user_id",
        back_populates="family_user",
    )


class Role(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    users: Mapped[list["UserRoleLink"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class UserRoleLink(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "user_role_links"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role_links_user_role"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="roles")
    role: Mapped["Role"] = relationship(back_populates="users")


if TYPE_CHECKING:
    from app.models.binding import ElderFamilyBinding
