"""简历管理 API。"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from sqlalchemy import or_

from app.api.deps import CurrentUser, DbSession, can_see_resume
from app.core.config import get_settings
from app.models.notification import Notification
from app.models.resume import Resume, ResumeChannel, ResumeSource
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.resume import ResumeCreate, ResumeOut, ResumeUpdate

router = APIRouter()


def _to_out(r: Resume) -> ResumeOut:
    return ResumeOut(
        id=r.id,
        name=r.name,
        chan=r.chan,
        pos=r.pos,
        owner_id=r.owner_id,
        owner_name=r.owner.name if r.owner else "",
        current_dept_id=r.current_dept_id,
        current_dept_name=r.current_dept_rel.name if r.current_dept_rel else "",
        source=r.source,
        by_user_id=r.by_user_id,
        by_user_name=None,  # 简化：需要时再 join
        file_path=r.file_path,
        raw_text=r.raw_text,
        keywords=r.keywords or [],
        traits=r.traits or [],
        exp_base=r.exp_base,
        education=r.education or [],
        experience=r.experience or [],
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.get("", response_model=PaginatedResponse[ResumeOut])
def list_resumes(
    db: DbSession,
    user: CurrentUser,
    chan: ResumeChannel | None = Query(None),
    q: str | None = Query(None),
    owner_id: str | None = Query(None),
    page: int = 1,
    page_size: int = 50,
) -> PaginatedResponse[ResumeOut]:
    """列出可见范围内的简历。"""
    query = db.query(Resume)

    # 角色权限过滤
    from app.models.user import Role
    if user.role in (Role.ADMIN, Role.HRD):
        pass  # 看全部
    elif user.role == Role.HRBP:
        query = query.filter(Resume.owner_id == user.id)
    elif user.role == Role.SOCIAL_LEAD:
        query = query.filter(Resume.chan == ResumeChannel.SOCIAL)
    elif user.role == Role.CAMPUS_LEAD:
        query = query.filter(Resume.chan == ResumeChannel.CAMPUS)

    if chan:
        query = query.filter(Resume.chan == chan)
    if owner_id:
        query = query.filter(Resume.owner_id == owner_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Resume.name.ilike(like),
                Resume.pos.ilike(like),
                Resume.keywords.cast_to_array().any_op("?") if False else False,  # 简化
            )
        )
        # 简化搜索：直接对 name/pos 做包含
        query = db.query(Resume).filter(
            or_(Resume.name.ilike(like), Resume.pos.ilike(like))
        )

    total = query.count()
    items = (
        query.order_by(Resume.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse[ResumeOut](
        items=[_to_out(r) for r in items], total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResumeOut, status_code=201)
def create_resume(
    payload: ResumeCreate, db: DbSession, user: CurrentUser
) -> ResumeOut:
    """手动创建简历（用于批量导入或初始化）。"""
    rid = payload.id or f"r-{int(datetime.utcnow().timestamp() * 1000)}"
    if db.get(Resume, rid):
        raise HTTPException(409, "简历 ID 已存在")
    r = Resume(
        id=rid,
        name=payload.name,
        chan=payload.chan,
        pos=payload.pos,
        owner_id=user.id,
        current_dept_id=payload.current_dept_id,
        source=payload.source,
        by_user_id=payload.by_user_id,
        keywords=payload.keywords,
        traits=payload.traits,
        exp_base=payload.exp_base,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _to_out(r)


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: str, db: DbSession, user: CurrentUser) -> ResumeOut:
    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权查看该简历")
    return _to_out(r)


@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: str, payload: ResumeUpdate, db: DbSession, user: CurrentUser
) -> ResumeOut:
    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if r.owner_id != user.id and user.role.value not in ("admin", "hrd"):
        raise HTTPException(403, "只能修改本人名下的简历")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return _to_out(r)


@router.delete("/{resume_id}", response_model=MessageResponse)
def delete_resume(
    resume_id: str, db: DbSession, user: CurrentUser
) -> MessageResponse:
    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if r.owner_id != user.id and user.role.value not in ("admin", "hrd"):
        raise HTTPException(403, "只能删除本人名下的简历")
    db.delete(r)
    db.commit()
    return MessageResponse(message="已删除")


@router.post("/recommend/{resume_id}/to/{dept_id}", response_model=MessageResponse)
def recommend_to_dept(
    resume_id: str, dept_id: str, db: DbSession, user: CurrentUser
) -> MessageResponse:
    """将简历推荐到某部门 HRBP 名下。"""
    from app.models.department import Department

    r = db.get(Resume, resume_id)
    if not r:
        raise HTTPException(404, "简历不存在")
    if not can_see_resume(user, r.owner_id, r.chan.value, r.current_dept_id):
        raise HTTPException(403, "无权操作该简历")
    d = db.get(Department, dept_id)
    if not d:
        raise HTTPException(404, "部门不存在")

    # 创建一份"归属对方"的新简历副本
    new_id = f"r-{int(datetime.utcnow().timestamp() * 1000)}"
    clone = Resume(
        id=new_id,
        name=r.name,
        chan=r.chan,
        pos=r.pos,
        owner_id=d.hrbp_id,
        current_dept_id=d.id,
        source=ResumeSource.RECOMMEND,
        by_user_id=user.id,
        keywords=r.keywords,
        traits=r.traits,
        exp_base=r.exp_base,
        raw_text=r.raw_text,
        file_path=r.file_path,
    )
    db.add(clone)
    # 通知对方
    notif = Notification(
        id=f"n-{int(datetime.utcnow().timestamp() * 1000)}",
        to_user_id=d.hrbp_id,
        from_user_id=user.id,
        type="recommend",
        title=f"新简历推荐：{r.name}",
        content=f"{user.name}（{user.role.value}）把 {r.name} 推荐到了你名下",
        resume_id=new_id,
    )
    db.add(notif)
    db.commit()
    return MessageResponse(message=f"已推荐到「{d.name}」并通知 HRBP")


@router.post("/upload", response_model=MessageResponse)
async def upload_resume(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(...),
    chan: ResumeChannel = ResumeChannel.SOCIAL,
    current_dept_id: str = Query(...),
) -> MessageResponse:
    """上传 PDF 简历，存到本地（后续 AI 解析在 /analysis 触发）。"""
    s = get_settings()
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "只支持 PDF 文件")
    content = await file.read()
    if len(content) > s.max_resume_size_mb * 1024 * 1024:
        raise HTTPException(400, f"文件超过 {s.max_resume_size_mb}MB")
    save_dir = s.resume_storage_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{int(datetime.utcnow().timestamp() * 1000)}_{file.filename}"
    fpath = save_dir / fname
    fpath.write_bytes(content)
    # 创建简历记录
    rid = f"r-{int(datetime.utcnow().timestamp() * 1000)}"
    r = Resume(
        id=rid,
        name=file.filename.rsplit(".", 1)[0],
        chan=chan,
        pos="待解析",
        owner_id=user.id,
        current_dept_id=current_dept_id,
        source=ResumeSource.IMPORT,
        file_path=str(fpath),
    )
    db.add(r)
    db.commit()
    return MessageResponse(message="上传成功，AI 解析中", detail=rid)