"""安全模块：JWT + 密码哈希。"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    """bcrypt 哈希密码。"""
    # bcrypt 限制 72 字节，超出截断
    pwd = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验密码。"""
    pwd = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pwd, hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    subject: str | int,
    extra: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """生成 JWT。"""
    s = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(hours=s.jwt_expire_hours)
    expire = datetime.now(timezone.utc) + expires_delta
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    """解码 JWT，失败返回 None。"""
    s = get_settings()
    try:
        return jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
    except JWTError:
        return None