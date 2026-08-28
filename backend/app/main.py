import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_v1_router, root_router
from app.core.config import settings
from app.core.exceptions import BaseAPIException
from app.core.logging import get_logger, setup_logging

setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger("app_main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown procedures."""
    logger.info("application_startup", app_env=settings.APP_ENV)
    yield
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Production-quality LinkedIn Profile API reverse-engineered with direct HTTP requests. "
        "No browser automation (Selenium/Playwright) used."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-ten-inky-63.vercel.app","http://localhost:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    """Middleware for attaching a unique request_id, timing requests,
    and writing structured JSON logs.
    """
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]

    request.state.request_id = request_id

    # Bind request_id to structlog contextvars for downstream automatic log injection
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.perf_counter()
    logger.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
            error=str(exc),
        )
        raise exc


@app.exception_handler(BaseAPIException)
async def custom_api_exception_handler(request: Request, exc: BaseAPIException):
    """Global exception handler for application domain exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        "api_exception_handled",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Fallback handler for unhandled exceptions, hiding stack traces from clients."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error("unhandled_exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
            },
            "request_id": request_id,
        },
    )


# Include routers
app.include_router(root_router)
app.include_router(api_v1_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.APP_ENV == "development"),
    )
