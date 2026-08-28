from fastapi import APIRouter

from app.api.health import router as health_router
from app.features.profile.router import router as profile_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(profile_router)

# Also expose health endpoint at root /health as requested by spec
root_router = APIRouter()
root_router.include_router(health_router)
