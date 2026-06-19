"""AI 分析相关 API。"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.models.position import Position, PositionStatus
from app.models.resume import Resume
from app.models.user import User
from app.schemas.position import AnalysisResult
from app.schemas.resume import QuestionItem, QuestionSet
from app.services.auth import can_see_resume, get_current_user
from app.services.llm import chat_llm

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ 本地规则版（无 API Key 时的 fallback）============

def _analyze_local(resume: Resume, pos: Position) -> AnalysisResult:
    """本地版分析：关键词重叠 + 隐性权重 + 经验分。"""
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
    implicit = round(sum(t["w"] for t in imp_tags if t["t"] in (resume.traits or [])]) / total_w * 100)

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
    """本地版面试题生成（规则模板）。"""
    k = (resume.keywords or [pos.keywords[0] if pos.keywords else "相关技术"])[0]
    high = (resume.exp_base or 70) >= 82
    return QuestionSet(
        专业=[
            QuestionItem(q=f"请描述一次你在 {k} 方向做过的最复杂优化，瓶颈如何定位与解决？", why="技术深度与问题定位", lvl="核心"),
            QuestionItem(q=f"针对「{pos.name}」谈谈 {' / '.join((pos.keywords or ['相关'])[:2])} 的工程实践", why="匹配 JD 关键词", lvl="核心"),
            QuestionItem(q="遇到大规模系统中某节点异常，你的排查思路是什么？", why="系统化工程思维", lvl="进阶"),
            *([QuestionItem(q="你如何评估一项新技术方案的收益与上线风险？", why="高潜候选人加测", lvl="拔高")] if high else []),
        ],
        主管=[
            QuestionItem(q="讲一个你推动跨团队协作落地的项目，最大阻力与处理方式", why="协作与落地能力", lvl="行为"),
            QuestionItem(q=f"你为什么选择「{pos.name}」，未来 3 年的规划是什么？", why="动机与稳定性", lvl="动机"),
            QuestionItem(q="当技术方案与上级判断不一致时，你会怎么做？", why="成熟度与沟通", lvl="行为"),
        ],
        资格=[
            QuestionItem(q="核对学历/履历真实性，确认在职状态与竞业限制", why="背调前置确认", lvl="合规"),
            QuestionItem(q="确认期望薪酬区间与到岗时间", why="流程信息", lvl="流程"),
            QuestionItem(q="是否接受出差/驻场及加班强度预期", why="岗位硬性条件", lvl="流程"),
        ],
    )


# ============ AI 增强版（接 LLM）============

ANALYZE_PROMPT = """你是资深的技术招聘专家。请基于候选人和岗位的客观数据，**只做总结和点评**，不要修改任何数字（数字部分由系统算）。

候选人：{name}（{chan}，意向岗位：{resume_pos}）
简历关键词：{resume_keywords}
简历隐性特征：{resume_traits}
基础经验分：{exp_base}

岗位：{pos_name}（{chan}，{level}）
岗位关键词：{pos_keywords}
岗位隐性标签权重：{implicit}

系统算分结果：
- 技能匹配 {skill}（命中 {k_hit}，未命中 {k_miss}）
- 经验匹配 {exp}
- 隐性要求 {implicit_score}（命中 {t_hit}，未命中 {t_miss}）
- 总分 {total}

请用 1-2 句话写一段**有判断、有洞察**的总结，重点指出：
1. 候选人最大的优势是什么
2. 最大的风险/短板是什么
3. 建议下一步怎么推进（强项推进 / 进入面试 / 谨慎考虑）

风格：专业、客观、有温度。150 字以内。

只返回总结文字，不要其他内容。"""


async def _analyze_with_llm(resume: Resume, pos: Position, local: AnalysisResult) -> AnalysisResult:
    """用 LLM 重新生成 summary 部分。"""
    prompt = ANALYZE_PROMPT.format(
        name=resume.name,
        chan=resume.chan.value,
        resume_pos=resume.pos,
        resume_keywords=", ".join(resume.keywords or []),
        resume_traits=", ".join(resume.traits or []),
        exp_base=resume.exp_base,
        pos_name=pos.name,
        level=pos.level,
        pos_keywords=", ".join(pos.keywords or []),
        implicit=json.dumps(pos.implicit or [], ensure_ascii=False),
        skill=local.skill,
        exp=local.exp,
        implicit_score=local.implicit,
        total=local.total,
        k_hit=", ".join(local.k_hit) or "（无）",
        k_miss=", ".join(local.k_miss) or "（无）",
        t_hit=", ".join(local.t_hit) or "（无）",
        t_miss=", ".join(local.t_miss) or "（无）",
    )
    try:
        summary = chat_llm(
            messages=[
                {"role": "system", "content": "你是算力事业部的高级招聘专家，回复简洁专业。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        # 清理可能的多余空白
        summary = summary.strip().strip('"').strip("「」").strip()
        local.summary = summary
    except Exception as e:
        logger.warning(f"AI 总结失败，使用本地版本: {e}")
    return local


QUESTIONS_PROMPT = """你是算力事业部的资深面试官。请基于以下候选人 + 岗位信息，生成三轮面试题。

候选人：{name}（{chan}，{exp_years}级别）
- 技能关键词：{keywords}
- 隐性特征：{traits}
- 意向岗位：{resume_pos}

目标岗位：{pos_name}（{level}）
- 岗位关键词：{pos_keywords}
- 岗位职责：{duties}
- 硬性要求：{must}

请生成三轮面试题，每轮 3-4 道题，每题包含 q（问题）、why（考察点）、lvl（核心/进阶/拔高/行为/动机/合规/流程）三个字段。

要求：
- 题目要**结合候选人背景和岗位 JD**，不是泛泛的模板题
- 专业题考察技术深度和系统能力
- 主管题考察协作、动机、成熟度
- 资格题考察背调和流程信息
- 题目难度根据候选人经验分自适应：高分候选人加 1 道拔高题

严格按以下 JSON 格式返回（不要任何额外文字、不要 markdown 包裹）：
{{
  "专业": [{{"q": "...", "why": "...", "lvl": "核心"}}, ...],
  "主管": [{{"q": "...", "why": "...", "lvl": "行为"}}, ...],
  "资格": [{{"q": "...", "why": "...", "lvl": "流程"}}, ...]
}}"""


async def _questions_with_llm(resume: Resume, pos: Position) -> QuestionSet:
    """用 LLM 生成面试题。"""
    exp = resume.exp_base or 70
    exp_years = "高级" if exp >= 85 else "中级" if exp >= 70 else "初级"
    prompt = QUESTIONS_PROMPT.format(
        name=resume.name,
        chan=resume.chan.value,
        exp_years=exp_years,
        keywords=", ".join(resume.keywords or []),
        traits=", ".join(resume.traits or []),
        resume_pos=resume.pos,
        pos_name=pos.name,
        level=pos.level,
        pos_keywords=", ".join(pos.keywords or []),
        duties="; ".join(pos.duties or []),
        must="; ".join(pos.must or []),
    )
    raw = chat_llm(
        messages=[
            {"role": "system", "content": "你只输出严格 JSON，不输出其他内容。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    # 清理 markdown 包裹
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(l for l in lines if not l.strip().startswith("```"))
        raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw)
        return QuestionSet(
            专业=[QuestionItem(**q) for q in data.get("专业", [])],
            主管=[QuestionItem(**q) for q in data.get("主管", [])],
            资格=[QuestionItem(**q) for q in data.get("资格", [])],
        )
    except Exception as e:
        logger.warning(f"AI 面试题解析失败，降级到本地版本: {e}")
        return _questions_local(resume, pos)


# ============ 路由 ============

@router.post("/match/{resume_id}/{pos_id}", response_model=AnalysisResult)
async def match_resume_position(
    resume_id: str,
    pos_id: str,
    db: DbSession,
    user: Annotated[User, Depends(get_current_user)],
    use_llm: bool = True,
) -> AnalysisResult:
    """简历 vs 岗位匹配分析。

    use_llm=true 且配置了 API Key 时，会用 LLM 重写 summary。
    评分数字（skill/exp/implicit/total）由本地规则算，不变。
    """
    r = db.get(Resume, resume_id)
    p = db.get(Position, pos_id)
    if not r or not p:
        raise HTTPException(404, "简历或岗位不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")
    result = _analyze_local(r, p)
    if use_llm:
        result = await _analyze_with_llm(r, p, result)
    return result


@router.post("/questions/{resume_id}/{pos_id}", response_model=QuestionSet)
async def generate_questions(
    resume_id: str,
    pos_id: str,
    db: DbSession,
    user: Annotated[User, Depends(get_current_user)],
    use_llm: bool = True,
) -> QuestionSet:
    """生成三轮面试题。use_llm=true 时用 LLM 生成。"""
    r = db.get(Resume, resume_id)
    p = db.get(Position, pos_id)
    if not r or not p:
        raise HTTPException(404, "简历或岗位不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")
    if use_llm:
        return await _questions_with_llm(r, p)
    return _questions_local(r, p)


@router.post("/route/{resume_id}")
def route_resume(
    resume_id: str, db: DbSession, user: Annotated[User, Depends(get_current_user)]
) -> list[dict]:
    """智能分流：给该简历推荐部门 + 岗位。"""
    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")

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
                "summary": a.summary,
            }
    return sorted(by_dept.values(), key=lambda x: -x["score"])


@router.post("/parse-resume/{resume_id}")
async def parse_resume_with_llm(
    resume_id: str,
    db: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """触发 LLM 对简历做结构化提取（基于已上传的 PDF 文本）。"""
    from app.services.pdf_parser import extract_structured_with_llm
    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if not r.raw_text:
        raise HTTPException(400, "该简历没有原文，请先上传 PDF")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权访问")
    try:
        data = extract_structured_with_llm(r.raw_text)
        # 写回数据库
        if data.get("name") and data["name"] != r.name:
            r.name = data["name"]
        if data.get("keywords"):
            r.keywords = data["keywords"]
        if data.get("traits"):
            r.traits = data["traits"]
        if isinstance(data.get("exp_base"), int):
            r.exp_base = data["exp_base"]
        if data.get("education"):
            r.education = data["education"]
        if data.get("experience"):
            r.experience = data["experience"]
        db.commit()
        return {"message": "AI 解析完成", "data": data}
    except Exception as e:
        raise HTTPException(500, f"AI 解析失败: {str(e)}")