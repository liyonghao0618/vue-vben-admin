import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.constants.roles import UserRole
from app.core.deps import get_current_user, require_roles
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.business import LogoutResponse, RefreshTokenRequest, RefreshTokenResponse
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.auth import authenticate_user, refresh_user_token, register_user
from app.services.business import list_roles

router = APIRouter()


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.post("/login", summary="账号登录", response_model=ApiResponse)
async def login(payload: LoginRequest, request: Request) -> ApiResponse:
    token_info = authenticate_user(payload.username, payload.password)
    return ApiResponse(data=token_info.model_dump(), meta=response_meta(request))


@router.post("/register", summary="角色化注册", response_model=ApiResponse)
async def register(payload: RegisterRequest, request: Request) -> ApiResponse:
    data = register_user(payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/me", summary="当前用户信息", response_model=ApiResponse)
async def me(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=user.model_dump(), meta=response_meta(request))


@router.post("/logout", summary="退出登录", response_model=ApiResponse)
async def logout(request: Request) -> ApiResponse:
    return ApiResponse(data=LogoutResponse().model_dump(), meta=response_meta(request))


@router.post("/refresh", summary="刷新 access token", response_model=ApiResponse)
async def refresh_token(
    request: Request,
    _: RefreshTokenRequest,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    token, expires_at = refresh_user_token(user)
    data = RefreshTokenResponse(access_token=token, expires_in=expires_at).model_dump()
    return ApiResponse(data=data, meta=response_meta(request))


@router.get("/roles", summary="角色信息列表", response_model=ApiResponse)
async def roles(
    request: Request,
    _: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_roles()],
        meta=response_meta(request),
    )


@router.get("/admin-permissions", summary="管理员权限探针", response_model=ApiResponse)
async def admin_permissions_probe(
    request: Request,
    user: Annotated[UserProfile, Depends(require_roles(UserRole.ADMIN))],
) -> ApiResponse:
    return ApiResponse(
        data={
            "user": user.model_dump(),
            "message": "管理员角色校验通过",
        },
        meta=response_meta(request),
    )
