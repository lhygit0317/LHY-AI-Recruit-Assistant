"""API 依赖注入：当前用户、权限检查。"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """从 JWT 解析当前用户。"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token 格式错误")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已停用")
    return user


def require_roles(*roles: Role):
    """要求特定角色才能访问。"""
    def _check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"当前角色 {user.role.value} 无权访问",
            )
        return user
    return _check


# 常用权限组合
require_admin = require_roles(Role.ADMIN)
require_admin_or_hrd = require_roles(Role.ADMIN, Role.HRD)
require_can_config = require_roles(Role.ADMIN, Role.HRD, Role.HRBP)
require_can_users = require_roles(Role.ADMIN)


def can_see_resume(viewer: User, resume_owner_id: str, resume_chan: str, resume_dept: str) -> bool:
    """根据角色判断能否看到某份简历。

    规则（对应原 HTML）：
    - admin / hrd: 看全部
    - hrbp: 只看本人名下（含被推荐到名下）
    - social_lead: 看所有社招
    - campus_lead: 看所有校招
    """
    if viewer.role in (Role.ADMIN, Role.HRD):
        return True
    if viewer.role == Role.HRBP:
        return resume_owner_id == viewer.id
    if viewer.role == Role.SOCIAL_LEAD:
        return resume_chan == "社招"
    if viewer.role == Role.CAMPUS_LEAD:
        return resume_chan == "校招"
    return False


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]