"""部门管理 API。"""

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbSession
from app.models.department import Department
from app.models.position import Position
from app.schemas.common import MessageResponse
from app.schemas.department import DepartmentCreate, DepartmentOut, DepartmentUpdate

router = APIRouter()


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: DbSession, _: CurrentUser) -> list[DepartmentOut]:
    """部门关系表 - 全员可见。"""
    depts = db.query(Department).order_by(Department.id).all()
    out = []
    for d in depts:
        out.append(
            DepartmentOut(
                id=d.id,
                name=d.name,
                hrbp_id=d.hrbp_id,
                mgr=d.mgr,
                cadres=[c for c in d.cadres.split(",") if c],
                created_at=d.created_at,
                position_count=len(d.positions),
            )
        )
    return out


@router.post("", response_model=DepartmentOut, status_code=201)
def create_dept(payload: DepartmentCreate, db: DbSession, _: CurrentUser) -> DepartmentOut:
    if db.get(Department, payload.id):
        raise HTTPException(409, "部门 ID 已存在")
    d = Department(
        id=payload.id,
        name=payload.name,
        hrbp_id=payload.hrbp_id,
        mgr=payload.mgr,
        cadres=",".join(payload.cadres),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return DepartmentOut(
        id=d.id, name=d.name, hrbp_id=d.hrbp_id, mgr=d.mgr,
        cadres=payload.cadres, created_at=d.created_at, position_count=0,
    )


@router.patch("/{dept_id}", response_model=DepartmentOut)
def update_dept(
    dept_id: str, payload: DepartmentUpdate, db: DbSession, _: CurrentUser
) -> DepartmentOut:
    d = db.get(Department, dept_id)
    if not d:
        raise HTTPException(404, "部门不存在")
    data = payload.model_dump(exclude_unset=True)
    if "cadres" in data:
        d.cadres = ",".join(data.pop("cadres"))
    for k, v in data.items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return DepartmentOut(
        id=d.id, name=d.name, hrbp_id=d.hrbp_id, mgr=d.mgr,
        cadres=[c for c in d.cadres.split(",") if c],
        created_at=d.created_at, position_count=len(d.positions),
    )


@router.delete("/{dept_id}", response_model=MessageResponse)
def delete_dept(dept_id: str, db: DbSession, _: CurrentUser) -> MessageResponse:
    d = db.get(Department, dept_id)
    if not d:
        raise HTTPException(404, "部门不存在")
    # 检查是否有关联岗位
    if db.query(Position).filter(Position.department_id == dept_id).count() > 0:
        raise HTTPException(400, "该部门下还有岗位，请先删除或转移")
    db.delete(d)
    db.commit()
    return MessageResponse(message="已删除")