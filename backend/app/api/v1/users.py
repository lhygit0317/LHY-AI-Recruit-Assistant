"""用户管理 API。"""

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DbSession, require_admin, require_can_users
from app.core.security import hash_password
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserOut])
def list_users(
    db: DbSession,
    _: User = require_can_users,
    q: str | None = Query(None, description="搜索 姓名/工号/部门"),
    page: int = 1,
    page_size: int = 50,
) -> PaginatedResponse[UserOut]:
    query = db.query(User)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (User.name.ilike(like)) | (User.id.ilike(like)) | (User.dept.ilike(like))
        )
    total = query.count()
    users = query.order_by(User.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse[UserOut](
        items=[UserOut.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate, db: DbSession, _: User = require_admin
) -> UserOut:
    if db.get(User, payload.id):
        raise HTTPException(409, "工号已存在")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(409, "邮箱已存在")
    user = User(
        id=payload.id,
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        dept=payload.dept,
        status=payload.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: DbSession, _: User = require_can_users) -> UserOut:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    return UserOut.model_validate(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str, payload: UserUpdate, db: DbSession, _: User = require_admin
) -> UserOut:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        user.hashed_password = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: str, db: DbSession, _: User = require_admin) -> MessageResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    # 软删除：停用账号
    user.is_active = False
    user.status = "已停用"
    db.commit()
    return MessageResponse(message="已停用账号")