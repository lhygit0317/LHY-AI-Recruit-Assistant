"""FastAPI 启动入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import (  # noqa: F401 触发所有 model 注册
    Department, Notification, Position, Resume, User,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时建表（开发环境用，生产用 Alembic）。"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="算力事业部 · 招聘智能助手 API",
    description="Recruit Assistant - 后端 API（2 周 MVP）",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {
        "app": "recruit-assistant",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=True)