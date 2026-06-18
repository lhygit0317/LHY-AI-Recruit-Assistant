"""通用 schema。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """通用消息响应。"""
    message: str = "ok"
    detail: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应。"""
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20