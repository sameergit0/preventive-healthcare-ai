from fastapi import APIRouter
from app.api.v1.endpoints import auth, profile, health_metrics, analytics

api_router = APIRouter()

api_router.include_router(router=auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(router=profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(router=health_metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(router=analytics.router, prefix="/analytics", tags=["analytics"])
