"""岗位管理 API。"""

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, DbSession, require_can_config
from app.models.department import Department
from app.models.position import Position, PositionStatus
from app.schemas.common import MessageResponse
from app.schemas.position import (
    ImplicitTag,
    PositionCreate,
    PositionOut,
    PositionUpdate,
)

router = APIRouter()


def _to_out(p: Position, dept_name: str = "") -> PositionOut:
    return PositionOut(
        id=p.id,
        name=p.name,
        chan=p.chan,
        level=p.level,
        department_id=p.department_id,
        department_name=dept_name,
        duties=p.duties or [],
        must=p.must or [],
        keywords=p.keywords or [],
        implicit=[ImplicitTag(**t) for t in (p.implicit or [])],
        status=p.status,
        created_at=p.created_at,
    )


@router.get("", response_model=list[PositionOut])
def list_positions(
    db: DbSession,
    _: CurrentUser,
    chan: str | None = Query(None, description="社招/校招"),
    active_only: bool = Query(False),
) -> list[PositionOut]:
    q = db.query(Position).join(Department, Position.department_id == Department.id)
    if chan:
        q = q.filter(Position.chan == chan)
    if active_only:
        q = q.filter(Position.status == PositionStatus.ON)
    return [_to_out(p, p.department.name) for p in q.all()]


@router.post("", response_model=PositionOut, status_code=201)
def create_position(
    payload: PositionCreate, db: DbSession, _: CurrentUser = require_can_config
) -> PositionOut:
    if db.get(Position, payload.id):
        raise HTTPException(409, "岗位 ID 已存在")
    if not db.get(Department, payload.department_id):
        raise HTTPException(400, "部门不存在")
    p = Position(
        id=payload.id,
        name=payload.name,
        chan=payload.chan,
        level=payload.level,
        department_id=payload.department_id,
        status=payload.status,
        duties=payload.duties,
        must=payload.must,
        keywords=payload.keywords,
        implicit=[t.model_dump() for t in payload.implicit],
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _to_out(p, p.department.name)


@router.get("/{pos_id}", response_model=PositionOut)
def get_position(pos_id: str, db: DbSession, _: CurrentUser) -> PositionOut:
    p = db.get(Position, pos_id)
    if not p:
        raise HTTPException(404, "岗位不存在")
    return _to_out(p, p.department.name)


@router.patch("/{pos_id}", response_model=PositionOut)
def update_position(
    pos_id: str,
    payload: PositionUpdate,
    db: DbSession,
    _: CurrentUser = require_can_config,
) -> PositionOut:
    p = db.get(Position, pos_id)
    if not p:
        raise HTTPException(404, "岗位不存在")
    data = payload.model_dump(exclude_unset=True)
    if "implicit" in data:
        data["implicit"] = [t.model_dump() if hasattr(t, "model_dump") else t for t in data["implicit"]]
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _to_out(p, p.department.name)


@router.post("/{pos_id}/tags", response_model=PositionOut)
def add_implicit_tag(
    pos_id: str, tag: ImplicitTag, db: DbSession, _: CurrentUser = require_can_config
) -> PositionOut:
    """添加一个隐性标签。"""
    p = db.get(Position, pos_id)
    if not p:
        raise HTTPException(404, "岗位不存在")
    tags = list(p.implicit or [])
    if any(t["t"] == tag.t for t in tags):
        raise HTTPException(409, "标签已存在")
    tags.append(tag.model_dump())
    p.implicit = tags
    db.commit()
    db.refresh(p)
    return _to_out(p, p.department.name)


@router.delete("/{pos_id}/tags/{tag_name}", response_model=PositionOut)
def remove_implicit_tag(
    pos_id: str, tag_name: str, db: DbSession, _: CurrentUser = require_can_config
) -> PositionOut:
    p = db.get(Position, pos_id)
    if not p:
        raise HTTPException(404, "岗位不存在")
    tags = [t for t in (p.implicit or []) if t["t"] != tag_name]
    p.implicit = tags
    db.commit()
    db.refresh(p)
    return _to_out(p, p.department.name)


@router.post("/{pos_id}/toggle", response_model=MessageResponse)
def toggle_position(
    pos_id: str, db: DbSession, _: CurrentUser = require_can_config
) -> MessageResponse:
    """上架/下架。"""
    p = db.get(Position, pos_id)
    if not p:
        raise HTTPException(404, "岗位不存在")
    p.status = (
        PositionStatus.OFF if p.status == PositionStatus.ON else PositionStatus.ON
    )
    db.commit()
    return MessageResponse(message=f"已{'下架' if p.status == PositionStatus.OFF else '上架'}")


@router.delete("/{pos_id}", response_model=MessageResponse)
def delete_position(
    pos_id: str, db: DbSession, _: CurrentUser = require_can_config
) -> MessageResponse:
    p = db.get(Position, pos_id)
    if not p:
        raise HTTPException(404, "岗位不存在")
    db.delete(p)
    db.commit()
    return MessageResponse(message="已删除")