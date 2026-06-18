"""岗位 schemas。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.position import PositionStatus


class ImplicitTag(BaseModel):
    """隐性标签：标签 + 权重。"""
    t: str
    w: int = Field(ge=0, le=100, default=15)


class PositionBase(BaseModel):
    name: str
    chan: str  # 社招 / 校招
    level: str = ""
    department_id: str
    duties: list[str] = Field(default_factory=list)
    must: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    implicit: list[ImplicitTag] = Field(default_factory=list)


class PositionCreate(PositionBase):
    id: str
    status: PositionStatus = PositionStatus.ON


class PositionUpdate(BaseModel):
    name: str | None = None
    chan: str | None = None
    level: str | None = None
    department_id: str | None = None
    status: PositionStatus | None = None
    duties: list[str] | None = None
    must: list[str] | None = None
    keywords: list[str] | None = None
    implicit: list[ImplicitTag] | None = None


class PositionOut(PositionBase):
    id: str
    status: PositionStatus
    created_at: datetime
    department_name: str = ""

    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    """简历-岗位匹配分析结果。"""
    skill: int          # 技能匹配分 0-100
    exp: int            # 经验匹配分 0-100
    implicit: int       # 隐性要求分 0-100
    total: int          # 总分 0-100
    k_hit: list[str]    # 命中关键词
    k_miss: list[str]   # 未命中关键词
    t_hit: list[str]    # 命中隐性标签
    t_miss: list[str]   # 未命中隐性标签
    verdict: str        # 强烈推荐 / 建议进入面试 / 谨慎
    summary: str        # AI 生成的分析说明