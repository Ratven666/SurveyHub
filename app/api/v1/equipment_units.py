from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import EquipmentUnit

router = APIRouter(prefix="/equipment-units", tags=["equipment-units"])

UnitStatus = Literal["working", "broken", "maintenance", "decommissioned"]


class EquipmentUnitCreate(BaseModel):
    equipment_id: int
    serial_number: str | None = None
    status: UnitStatus = "working"


class EquipmentUnitUpdate(BaseModel):
    serial_number: str | None = None
    status: UnitStatus | None = None


class EquipmentUnitRead(BaseModel):
    id: int
    equipment_id: int
    serial_number: str | None
    status: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[EquipmentUnitRead])
def list_equipment_units(
    db: DbSession,
    equipment_id: int | None = None,
    status: str | None = None,
):
    q = db.query(EquipmentUnit)
    if equipment_id is not None:
        q = q.filter(EquipmentUnit.equipment_id == equipment_id)
    if status is not None:
        q = q.filter(EquipmentUnit.status == status)
    return q.all()


@router.post("/", response_model=EquipmentUnitRead, status_code=201)
def create_equipment_unit(data: EquipmentUnitCreate, db: DbSession):
    unit = EquipmentUnit(**data.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.get("/{unit_id}", response_model=EquipmentUnitRead)
def get_equipment_unit(unit_id: int, db: DbSession):
    unit = db.get(EquipmentUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="EquipmentUnit not found")
    return unit


@router.patch("/{unit_id}", response_model=EquipmentUnitRead)
def update_equipment_unit(unit_id: int, data: EquipmentUnitUpdate, db: DbSession):
    unit = db.get(EquipmentUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="EquipmentUnit not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=204)
def delete_equipment_unit(unit_id: int, db: DbSession):
    unit = db.get(EquipmentUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="EquipmentUnit not found")
    db.delete(unit)
    db.commit()
