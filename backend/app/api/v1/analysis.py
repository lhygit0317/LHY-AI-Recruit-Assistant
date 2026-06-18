"""AI 分析相关 API。"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession, can_see_resume
from app.models.position import Position
from app.models.resume import Resume
from app.schemas.position import AnalysisResult
from app.schemas.resume import QuestionItem, QuestionSet
from app.services.llm import chat_llm

logger = logging.getLogger(__name__)
router = APIRouter()


def _analyze_local(resume: Resume, pos: Position) -> AnalysisResult:
    """本地版分析（不上 LLM，规则匹配）—— 用于无 API Key 时的 fallback。"""
    pos_kw = pos.keywords or []
    r_kw = resume.keywords or []
    k_hit = [k for k in pos_kw if k in r_kw]
    k_miss = [k for k in pos_kw if k not in r_kw]
    skill = round(len(k_hit) / len(pos_kw) * 100) if pos_kw else 0

    exp = resume.exp_base or 70
    imp_tags = pos.implicit or []
    total_w = sum(t["w"] for t in imp_tags) or 1
    t_hit = [t["t"] for t in imp_tags if t["t"] in (resume.traits or [])]
    t_miss = [t["t"] for t in imp_tags if t["t"] not in (resume.traits or [])]
    implicit = round(sum(t["w"] for t in imp_tags if t["t"] in (resume.traits or [])) / total_w * 100)

    total = round(skill * 0.4 + exp * 0.25 + implicit * 0.35)
    if total >= 80:
        verdict, summary = "强烈推荐", "与该岗位高度匹配，建议优先推进。"
    elif total >= 65:
        verdict, summary = "建议进入面试", "基本匹配，建议进入面试进一步考察。"
    else:
        verdict, summary = "谨慎 / 暂不推荐", "匹配度偏低，建议谨慎或考虑其他岗位。"

    return AnalysisResult(
        skill=skill, exp=exp, implicit=implicit, total=total,
        k_hit=k_hit, k_miss=k_miss, t_hit=t_hit, t_miss=t_miss,
        verdict=verdict, summary=summary,
    )


def _questions_local(resume: Resume, pos: Position) -> QuestionSet:
    """本地版面试题生成。"""
    k = (resume.keywords or [pos.keywords[0] if pos.keywords else "相关技术"])[0]
    high = (resume.exp_base or 70) >= 82
    return QuestionSet(
        专业=[
            QuestionItem(q=f"请描述一次你在 {k} 方向做过的最复杂优化", why="技术深度", lvl="核心"),
            QuestionItem(q=f"针对「{pos.name}」谈谈 {' / '.join((pos.keywords or ['相关'])[:2])}", why="匹配 JD", lvl="核心"),
            QuestionItem(q="大规模系统中节点异常，你的排查思路？", why="系统化思维", lvl="进阶"),
            *([QuestionItem(q="如何评估新技术方案的收益与风险？", why="高潜拔高", lvl="拔高")] if high else []),
        ],
        主管=[
            QuestionItem(q="讲一个你推动跨团队协作的项目，最大阻力与处理", why="协作能力", lvl="行为"),
            QuestionItem(q=f"你为什么选择「{pos.name}」，未来 3 年规划？", why="动机与稳定性", lvl="动机"),
            QuestionItem(q="技术方案与上级判断不一致时你会怎么做？", why="成熟度", lvl="行为"),
        ],
        资格=[
            QuestionItem(q="核对学历/履历真实性，确认在职状态与竞业", why="背调", lvl="合规"),
            QuestionItem(q="确认期望薪酬与到岗时间", why="流程", lvl="流程"),
            QuestionItem(q="是否接受出差/驻场与加班强度", why="硬性条件", lvl="流程"),
        ],
    )


@router.post("/match/{resume_id}/{pos_id}", response_model=AnalysisResult)
def match_resume_position(
    resume_id: str, pos_id: str, db: DbSession, user: CurrentUser
) -> AnalysisResult:
    """简历 vs 岗位匹配分析。"""
    r = db.get(Resume, resume_id)
    p = db.get(Position, pos_id)
    if not r or not p:
        raise HTTPException(404, "简历或岗位不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")
    return _analyze_local(r, p)


@router.post("/questions/{resume_id}/{pos_id}", response_model=QuestionSet)
def generate_questions(
    resume_id: str, pos_id: str, db: DbSession, user: CurrentUser, use_llm: bool = True
) -> QuestionSet:
    """生成三轮面试题。

    use_llm=True 且配置了 API Key 时调用 LLM，否则用本地规则。
    """
    r = db.get(Resume, resume_id)
    p = db.get(Position, pos_id)
    if not r or not p:
        raise HTTPException(404, "简历或岗位不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")
    if not use_llm:
        return _questions_local(r, p)
    # LLM 调用（Day 8 实现）
    return _questions_local(r, p)


@router.post("/route/{resume_id}")
def route_resume(
    resume_id: str, db: DbSession, user: CurrentUser
) -> list[dict]:
    """智能分流：给该简历推荐部门 + 岗位。"""
    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")

    from app.models.position import PositionStatus
    cands = (
        db.query(Position)
        .filter(Position.chan == r.chan, Position.status == PositionStatus.ON)
        .all()
    )
    by_dept: dict[str, dict] = {}
    for p in cands:
        a = _analyze_local(r, p)
        d = p.department
        if not d:
            continue
        if d.id not in by_dept or a.total > by_dept[d.id]["score"]:
            by_dept[d.id] = {
                "dept_id": d.id,
                "dept_name": d.name,
                "hrbp_id": d.hrbp_id,
                "mgr": d.mgr,
                "cadres": [c for c in d.cadres.split(",") if c],
                "position_id": p.id,
                "position_name": p.name,
                "score": a.total,
            }
    return sorted(by_dept.values(), key=lambda x: -x["score"])