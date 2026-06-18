"""简历 schemas。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.resume import ResumeChannel, ResumeSource


class ResumeBase(BaseModel):
    name: str
    chan: ResumeChannel
    pos: str = "待定"
    current_dept_id: str
    keywords: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    exp_base: int = Field(ge=0, le=100, default=70)


class ResumeCreate(ResumeBase):
    """手动创建简历（不上传 PDF）。"""
    id: str | None = None
    source: ResumeSource = ResumeSource.IMPORT
    by_user_id: str | None = None


class ResumeImport(BaseModel):
    """上传 PDF + AI 解析后回填。"""
    file_path: str
    chan: ResumeChannel
    current_dept_id: str


class ResumeUpdate(BaseModel):
    name: str | None = None
    chan: ResumeChannel | None = None
    pos: str | None = None
    current_dept_id: str | None = None
    keywords: list[str] | None = None
    traits: list[str] | None = None
    exp_base: int | None = None


class ResumeOut(ResumeBase):
    id: str
    owner_id: str
    owner_name: str = ""
    current_dept_name: str = ""
    source: ResumeSource
    by_user_id: str | None = None
    by_user_name: str | None = None
    file_path: str | None = None
    raw_text: str | None = None
    education: list[dict] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionItem(BaseModel):
    """单个面试题。"""
    q: str        # 问题
    why: str      # 考察点
    lvl: str      # 等级：核心/进阶/拔高/行为/动机/合规/流程


class QuestionSet(BaseModel):
    """三轮面试题。"""
    专业: list[QuestionItem]
    主管: list[QuestionItem]
    资格: list[QuestionItem]