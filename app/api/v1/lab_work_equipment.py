from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import DbSession
from app.models import Equipment, LabWork, LabWorkEquipment

router = APIRouter(prefix="/lab-work-equipment", tags=["lab-work-equipment"])


class LinkCreate(BaseModel):
    lab_work_id: int
    equipment_id: int
    required_units: int = Field(default=1, ge=1)


class LinkUpdate(BaseModel):
    required_units: int = Field(ge=1)


class LinkRead(BaseModel):
    id: int
    lab_work_id: int
    equipment_id: int
    required_units: int
    model_config = {"from_attributes": True}


def _get_or_404(link_id: int, db: DbSession) -> LabWorkEquipment:
    obj = db.get(LabWorkEquipment, link_id)
    if not obj:
        raise HTTPException(404, "LabWorkEquipment link not found")
    return obj


@router.get("/", response_model=list[LinkRead])
def list_links(
    db: DbSession,
    lab_work_id: int | None = None,
    equipment_id: int | None = None,
):
    q = db.query(LabWorkEquipment)
    if lab_work_id is not None:
        q = q.filter(LabWorkEquipment.lab_work_id == lab_work_id)
    if equipment_id is not None:
        q = q.filter(LabWorkEquipment.equipment_id == equipment_id)
    return q.all()


@router.post("/", response_model=LinkRead, status_code=201)
def create_link(data: LinkCreate, db: DbSession):
    if not db.get(LabWork, data.lab_work_id):
        raise HTTPException(404, f"LabWork {data.lab_work_id} not found")
    if not db.get(Equipment, data.equipment_id):
        raise HTTPException(404, f"Equipment {data.equipment_id} not found")
    # Проверяем дубликат вручную — даём понятную ошибку вместо 500
    existing = (
        db.query(LabWorkEquipment)
        .filter_by(lab_work_id=data.lab_work_id, equipment_id=data.equipment_id)
        .first()
    )
    if existing:
        raise HTTPException(
            409,
            f"Equipment {data.equipment_id} already linked to LabWork {data.lab_work_id}",
        )
    obj = LabWorkEquipment(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.get("/{link_id}", response_model=LinkRead)
def get_link(link_id: int, db: DbSession):
    return _get_or_404(link_id, db)


@router.patch("/{link_id}", response_model=LinkRead)
def update_link(link_id: int, data: LinkUpdate, db: DbSession):
    obj = _get_or_404(link_id, db)
    obj.required_units = data.required_units
    db.commit(); db.refresh(obj)
    return obj


@router.delete("/{link_id}", status_code=204)
def delete_link(link_id: int, db: DbSession):
    db.delete(_get_or_404(link_id, db)); db.commit()
