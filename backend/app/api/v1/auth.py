"""认证相关 API。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserOut
from app.services.auth import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """OAuth2 标准登录（username=工号, password=密码）。"""
    user = db.get(User, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="工号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    token = create_access_token(user.id, extra={"role": user.role.value, "name": user.name})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login-json", response_model=Token)
def login_json(
    payload: UserLogin, db: Annotated[Session, Depends(get_db)]
) -> Token:
    """JSON 登录（前端 axios 友好）。"""
    user = db.get(User, payload.user_id)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="工号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    token = create_access_token(user.id, extra={"role": user.role.value, "name": user.name})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    """当前登录用户。"""
    return user