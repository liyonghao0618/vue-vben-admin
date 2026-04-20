from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.constants.roles import UserRole
from app.core.security import decode_access_token
from app.schemas.user import UserProfile
from app.services.auth import get_user_by_id


def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Bearer Token",
        )
    return authorization.replace("Bearer ", "", 1).strip()


def get_current_user(token: Annotated[str, Depends(get_bearer_token)]) -> UserProfile:
    return get_current_user_from_token(token)


def get_current_user_from_token(token: str) -> UserProfile:
    payload = decode_access_token(token)
    user = get_user_by_id(payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已失效",
        )
    return user


def require_roles(*roles: UserRole) -> Callable[[UserProfile], UserProfile]:
    def checker(user: Annotated[UserProfile, Depends(get_current_user)]) -> UserProfile:
        if not set(roles).intersection(set(user.roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="当前角色无权访问该接口",
            )
        return user

    return checker
