"""用户 schemas。"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import Role


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Role = Role.HRBP
    dept: str = ""
    status: str = "在职"


class UserCreate(UserBase):
    id: str = Field(..., description="工号")
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: str | None = None
    role: Role | None = None
    dept: str | None = None
    status: str | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=6)


class UserOut(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    user_id: str  # 工号登录
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut