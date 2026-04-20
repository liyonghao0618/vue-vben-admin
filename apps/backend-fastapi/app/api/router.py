from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, bindings, chats, community, docs, elder, family, health, notifications, risk_alerts, risk_recognition

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(bindings.router, tags=["Bindings"])
api_router.include_router(risk_alerts.router, tags=["Risk Alerts"])
api_router.include_router(risk_recognition.router, tags=["Risk Recognition"])
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(chats.router, tags=["Chats"])
api_router.include_router(elder.router, tags=["Elder"])
api_router.include_router(family.router, tags=["Family"])
api_router.include_router(community.router, tags=["Community"])
api_router.include_router(admin.router, tags=["Admin"])
api_router.include_router(docs.router, prefix="/docs", tags=["Docs"])
