"""API 依赖注入：DB Session。"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

DbSession = Annotated[Session, Depends(get_db)]
""" 类型别名：直接 `db: DbSession` 就能注入 Session。"""