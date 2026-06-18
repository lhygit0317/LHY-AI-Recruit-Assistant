"""PDF 简历解析。"""

from __future__ import annotations

import logging

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def parse_resume_pdf(path: str) -> str:
    """提取 PDF 的纯文本内容。"""
    doc = fitz.open(path)
    try:
        text = "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()
    return text


def extract_structured_with_llm(text: str) -> dict:
    """用 LLM 从纯文本提取结构化信息（关键词/特征/经验分）。

    返回格式: {
        "name": "...",
        "keywords": ["...", "..."],
        "traits": ["...", "..."],
        "exp_base": 80,
        "education": [...],
        "experience": [...],
    }
    """
    from app.services.llm import chat_llm

    prompt = f"""请从以下简历文本中提取结构化信息，并以严格的 JSON 格式返回（不要任何额外说明文字）：

简历文本：
{text[:6000]}

返回 JSON 格式：
{{
  "name": "候选人姓名",
  "keywords": ["技能1", "技能2", "技能3", "技能4", "技能5"],
  "traits": ["特征1", "特征2", "特征3", "特征4"],
  "exp_base": 0-100 的整数（基础经验分）,
  "education": [{{"school": "学校", "degree": "学历", "major": "专业", "year": "年份"}}],
  "experience": [{{"company": "公司", "title": "职位", "duration": "时间段", "description": "简述"}}]
}}

只返回 JSON，不要其他内容。"""
    raw = chat_llm(
        messages=[
            {"role": "system", "content": "你是简历结构化专家，严格输出 JSON。"},
            {"role": "user", "content": prompt},
        ]
    )
    # 解析：去掉可能的 markdown 包裹
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    import json
    return json.loads(raw)