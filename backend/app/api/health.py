from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["General"])


class HealthResponse(BaseModel):
    status: str = "ok"


@router.get(
    "/",
    summary="Root API Info & Navigation",
    description="Returns API service information, status, and navigation links to documentation.",
)
async def root() -> dict[str, Any]:
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "description": "Reverse-engineered LinkedIn Profile API",
        "links": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
        },
        "endpoints": {
            "extract_profile": {
                "method": "POST",
                "path": "/api/v1/profile",
                "description": "Extract structured profile details from a LinkedIn URL",
                "sample_payload": {
                    "url": "https://www.linkedin.com/in/sundarpichai/"
                },
            }
        },
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns service status without calling LinkedIn endpoints.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
