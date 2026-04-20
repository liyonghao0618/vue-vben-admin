import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketException, status

from app.core.deps import get_current_user, get_current_user_from_token
from app.schemas.chat import ChatSendMessageRequest, CreateConversationRequest, MarkMessageReadRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.chat import (
    create_or_get_conversation,
    get_conversation_detail,
    get_unread_summary,
    list_conversations,
    list_online_states,
    manager,
    mark_messages_read,
    search_chat_users,
    send_message,
    websocket_loop,
)

router = APIRouter(prefix="/chats")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("/users/search", response_model=ApiResponse)
async def search_users(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    keyword: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in search_chat_users(user, keyword, limit)],
        meta=response_meta(request),
    )


@router.post("/conversations", response_model=ApiResponse)
async def create_conversation(
    payload: CreateConversationRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=create_or_get_conversation(user, payload).model_dump(), meta=response_meta(request))


@router.get("/conversations", response_model=ApiResponse)
async def get_conversations(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=[item.model_dump() for item in list_conversations(user)], meta=response_meta(request))


@router.get("/conversations/{conversation_id}", response_model=ApiResponse)
async def get_conversation(
    conversation_id: str,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse:
    return ApiResponse(
        data=get_conversation_detail(user, conversation_id, page, page_size).model_dump(),
        meta=response_meta(request),
    )


@router.post("/conversations/{conversation_id}/messages", response_model=ApiResponse)
async def post_message(
    conversation_id: str,
    payload: ChatSendMessageRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = send_message(user, conversation_id, payload)
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "message",
            "data": data.model_dump(),
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.post("/conversations/{conversation_id}/read", response_model=ApiResponse)
async def post_read(
    conversation_id: str,
    payload: MarkMessageReadRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = mark_messages_read(user, conversation_id, payload)
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "read",
            "data": {
                "conversation_id": conversation_id,
                "user_id": user.user_id,
                "last_read_message_id": payload.last_read_message_id,
                **data.model_dump(),
            },
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/unread-summary", response_model=ApiResponse)
async def unread_summary(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=get_unread_summary(user).model_dump(), meta=response_meta(request))


@router.get("/online-states", response_model=ApiResponse)
async def online_states(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    user_ids: list[str] = Query(default_factory=list),
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_online_states(user, user_ids or None)],
        meta=response_meta(request),
    )


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket, token: str) -> None:
    try:
        user = get_current_user_from_token(token)
    except Exception as exc:  # pragma: no cover
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from exc
    await websocket_loop(user, websocket)
