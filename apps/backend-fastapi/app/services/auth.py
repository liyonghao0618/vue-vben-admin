from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.constants.roles import UserRole
from app.core.security import create_access_token
from app.db.session import session_scope
from app.models import Role, User, UserRoleLink
from app.schemas.auth import LoginResponse, RegisterRequest, RegisterResponse
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


def register_user(payload: RegisterRequest) -> RegisterResponse:
    with session_scope() as session:
        existing_user = session.scalar(
            select(User).where(User.username == payload.username)
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已存在",
            )
        existing_phone = session.scalar(select(User).where(User.phone == payload.phone))
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="手机号已存在",
            )

        target_role = session.scalar(select(Role).where(Role.code == payload.role.value))
        if not target_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        user = User(
            id=f"u-{payload.role.value}-{uuid.uuid4().hex[:8]}",
            username=payload.username,
            password_hash=payload.password,
            display_name=payload.display_name,
            phone=payload.phone,
            status="active",
            is_verified=False,
            notes=(f"invite_code={payload.invite_code}" if payload.invite_code else None),
        )
        session.add(user)
        session.flush()
        session.add(
            UserRoleLink(
                id=f"url-{user.id}-{payload.role.value}",
                user_id=user.id,
                role_id=target_role.id,
            )
        )
        return RegisterResponse(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            phone=user.phone,
            roles=[payload.role],
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
