import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.constants.roles import UserRole
from app.core.deps import require_roles
from app.schemas.business import CallRecognitionRequest, RiskRecognitionResult, SmsRecognitionRequest
from app.schemas.common import ApiResponse, MetaPayload
from app.services.risk_recognition import recognize_call, recognize_call_audio, recognize_sms

router = APIRouter(prefix="/risk-recognition")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.post("/sms", summary="短信文本风险识别", response_model=ApiResponse)
async def post_sms_recognition(
    payload: SmsRecognitionRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN, UserRole.COMMUNITY, UserRole.ELDER, UserRole.FAMILY))],
) -> ApiResponse:
    result = RiskRecognitionResult(**recognize_sms(**payload.model_dump()))
    return ApiResponse(data=result.model_dump(), meta=response_meta(request))


@router.post("/call", summary="通话文本风险识别", response_model=ApiResponse)
async def post_call_recognition(
    payload: CallRecognitionRequest,
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN, UserRole.COMMUNITY, UserRole.ELDER, UserRole.FAMILY))],
) -> ApiResponse:
    result = RiskRecognitionResult(**recognize_call(**payload.model_dump()))
    return ApiResponse(data=result.model_dump(), meta=response_meta(request))


@router.post("/call-audio", summary="通话录音风险识别", response_model=ApiResponse)
async def post_call_audio_recognition(
    request: Request,
    _: Annotated[object, Depends(require_roles(UserRole.ADMIN, UserRole.COMMUNITY, UserRole.ELDER, UserRole.FAMILY))],
    audio_file: UploadFile = File(...),
    elder_user_id: str = Form(...),
    call_session_id: str | None = Form(default=None),
    caller_number: str | None = Form(default=None),
    duration_seconds: int | None = Form(default=None),
    occurred_at: str | None = Form(default=None),
) -> ApiResponse:
    content = await audio_file.read()
    result = RiskRecognitionResult(
        **recognize_call_audio(
            elder_user_id=elder_user_id,
            audio_content=content,
            filename=audio_file.filename or "call-audio.webm",
            call_session_id=call_session_id,
            caller_number=caller_number,
            duration_seconds=duration_seconds,
            occurred_at=occurred_at,
        )
    )
    return ApiResponse(data=result.model_dump(), meta=response_meta(request))
