from app.api.v1.endpoints import (
    auth, timezone, profile, health_metrics,
    lifestyle, analytics, medical_history
)
from fastapi import APIRouter


api_router = APIRouter()

api_router.include_router(router=auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(router=timezone.router, prefix="/timezones", tags=["timezones"])
api_router.include_router(router=profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(router=health_metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(router=lifestyle.router, prefix="/lifestyle", tags=["lifestyle"])
api_router.include_router(router=medical_history.router, prefix="/medical-history", tags=["medical_history"])
api_router.include_router(router=analytics.router, prefix="/analytics", tags=["analytics"])
