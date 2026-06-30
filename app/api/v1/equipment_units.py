from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from app.api.deps import DbSession
from app.models import Equipment, EquipmentUnit

STATUSES = Literal["working", "repair", "reserve", "broken", "decommissioned"]

router = APIRouter(prefix="/equipment-units", tags=["equipment-units"])


class UnitCreate(BaseModel):
    equipment_id: int
    name: str | None = None
    serial_number: str | None = None
    inventory_number: str | None = None
    status: STATUSES = "working"


class UnitUpdate(BaseModel):
    name: str | None = None
    serial_number: str | None = None
    inventory_number: str | None = None
    status: STATUSES | None = None


class UnitRead(BaseModel):
    id: int
    equipment_id: int
    name: str | None
    serial_number: str | None
    inventory_number: str | None
    status: str
    model_config = {"from_attributes": True}


def _get_or_404(unit_id: int, db: DbSession) -> EquipmentUnit:
    obj = db.get(EquipmentUnit, unit_id)
    if not obj:
        raise HTTPException(404, "EquipmentUnit not found")
    return obj


@router.get("/", response_model=list[UnitRead])
def list_units(
    db: DbSession,
    equipment_id: int | None = None,
    status: STATUSES | None = None,
):
    q = db.query(EquipmentUnit)
    if equipment_id is not None:
        if not db.get(Equipment, equipment_id):
            raise HTTPException(404, f"Equipment {equipment_id} not found")
        q = q.filter(EquipmentUnit.equipment_id == equipment_id)
    if status is not None:
        q = q.filter(EquipmentUnit.status == status)
    return q.order_by(EquipmentUnit.equipment_id, EquipmentUnit.id).all()


@router.get("/{unit_id}", response_model=UnitRead)
def get_unit(unit_id: int, db: DbSession):
    return _get_or_404(unit_id, db)


@router.post("/", response_model=UnitRead, status_code=201)
def create_unit(data: UnitCreate, db: DbSession):
    # Проверяем существование equipment_id
    if not db.get(Equipment, data.equipment_id):
        raise HTTPException(404, "Equipment type not found")

    obj = EquipmentUnit(**data.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        err = str(e.orig)
        if "serial_number" in err:
            raise HTTPException(409, "Serial number already exists")
        if "inventory_number" in err:
            raise HTTPException(409, "Inventory number already exists")
        raise HTTPException(409, "Duplicate value in unique field")
    db.refresh(obj)
    return obj


@router.patch("/{unit_id}", response_model=UnitRead)
def update_unit(unit_id: int, data: UnitUpdate, db: DbSession):
    obj = _get_or_404(unit_id, db)
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        err = str(e.orig)
        if "serial_number" in err:
            raise HTTPException(409, "Serial number already exists")
        if "inventory_number" in err:
            raise HTTPException(409, "Inventory number already exists")
        raise HTTPException(409, "Duplicate value in unique field")
    db.refresh(obj)
    return obj


@router.delete("/{unit_id}", status_code=204)
def delete_unit(unit_id: int, db: DbSession):
    db.delete(_get_or_404(unit_id, db)); db.commit()
