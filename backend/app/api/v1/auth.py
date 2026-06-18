"""认证相关 API。"""

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserOut

router = APIRouter()


@router.post("/login", response_model=Token)
def login(db: DbSession, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """OAuth2 标准登录（username=工号, password=密码）。

    也可以用 /login-json 接 JSON。
    """
    user = db.get(User, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="工号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    token = create_access_token(user.id, extra={"role": user.role.value, "name": user.name})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login-json", response_model=Token)
def login_json(db: DbSession, payload: UserLogin) -> Token:
    """JSON 登录（前端 axios 友好）。"""
    user = db.get(User, payload.user_id)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="工号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    token = create_access_token(user.id, extra={"role": user.role.value, "name": user.name})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    """当前登录用户。"""
    return user