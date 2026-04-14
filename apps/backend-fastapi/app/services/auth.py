from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.constants.roles import UserRole
from app.core.security import create_access_token
from app.db.session import session_scope
from app.models import User, UserRoleLink
from app.schemas.auth import LoginResponse
from app.schemas.user import UserProfile
from app.services.db_init import ROLE_DETAILS


def _build_user_profile(user: User) -> UserProfile:
    roles = [UserRole(link.role.code) for link in user.roles]
    permissions: list[str] = []
    for role in roles:
        permissions.extend(ROLE_DETAILS[role]["permissions"])
    unique_permissions = list(dict.fromkeys(str(item) for item in permissions))
    return UserProfile(
        user_id=user.id,
        username=user.username,
        display_name=user.display_name,
        phone=user.phone,
        roles=roles,
        permissions=unique_permissions,
    )


def authenticate_user(username: str, password: str) -> LoginResponse:
    with session_scope() as session:
        user = session.scalar(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRoleLink.role))
            .where(User.username == username)
        )
        if not user or user.password_hash != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        profile = _build_user_profile(user)
        token, expires_at = create_access_token(
            user_id=profile.user_id,
            username=profile.username,
            roles=[role.value for role in profile.roles],
        )
        return LoginResponse(
            access_token=token,
            refresh_token=f"refresh-{profile.user_id}",
            expires_in=expires_at,
            user_id=profile.user_id,
            username=profile.username,
            display_name=profile.display_name,
            roles=profile.roles,
        )


def refresh_user_token(user: UserProfile) -> tuple[str, int]:
    return create_access_token(
        user_id=user.user_id,
        username=user.username,
        roles=[role.value for role in user.roles],
    )


def get_user_by_id(user_id: str) -> UserProfile | None:
    with session_scope() as session:
        user = session.scalar(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRoleLink.role))
            .where(User.id == user_id)
        )
        if not user:
            return None
        return _build_user_profile(user)
