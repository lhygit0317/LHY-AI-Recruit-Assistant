"""部门 schemas。"""

from datetime import datetime

from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    name: str
    hrbp_id: str
    mgr: str = ""
    cadres: list[str] = Field(default_factory=list)


class DepartmentCreate(DepartmentBase):
    id: str


class DepartmentUpdate(BaseModel):
    name: str | None = None
    hrbp_id: str | None = None
    mgr: str | None = None
    cadres: list[str] | None = None


class DepartmentOut(DepartmentBase):
    id: str
    created_at: datetime
    position_count: int = 0

    class Config:
        from_attributes = True