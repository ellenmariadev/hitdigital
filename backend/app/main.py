import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import users
from app.cache import build_cache
from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.db.session import build_engine, build_session_factory, ping
from app.providers import build_provider
from app.services.user_service import UserService

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.debug)

    engine = build_engine()
    session_factory = build_session_factory(engine)
    provider = build_provider(settings)
    cache = build_cache(settings, session_factory)

    app.state.engine = engine
    app.state.provider = provider
    app.state.cache = cache
    app.state.user_service = UserService(provider=provider, cache=cache)

    logger.info("app_started", provider=settings.user_provider)
    try:
        yield
    finally:
        await provider.aclose()
        await engine.dispose()
        logger.info("app_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed")
            structlog.contextvars.clear_contextvars()
            raise

        response.headers["x-request-id"] = request_id
        logger.info(
            "request_completed",
            status=response.status_code,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        structlog.contextvars.clear_contextvars()
        return response

    app.include_router(users.router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/health/db")
    async def health_db(request: Request):
        try:
            await ping(request.app.state.engine)
            return {"database": "ok"}
        except Exception:
            return JSONResponse(status_code=503, content={"database": "error"})

    return app


app = create_app()
