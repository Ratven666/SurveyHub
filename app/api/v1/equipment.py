from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import Equipment

router = APIRouter(prefix="/equipment", tags=["equipment"])


class EquipmentCreate(BaseModel):
    name: str
    description: str | None = None


class EquipmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class EquipmentRead(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[EquipmentRead])
def list_equipment(db: DbSession):
    return db.query(Equipment).all()


@router.post("/", response_model=EquipmentRead, status_code=201)
def create_equipment(data: EquipmentCreate, db: DbSession):
    equipment = Equipment(**data.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.get("/{equipment_id}", response_model=EquipmentRead)
def get_equipment(equipment_id: int, db: DbSession):
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.patch("/{equipment_id}", response_model=EquipmentRead)
def update_equipment(equipment_id: int, data: EquipmentUpdate, db: DbSession):
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(equipment, field, value)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/{equipment_id}", status_code=204)
def delete_equipment(equipment_id: int, db: DbSession):
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    db.delete(equipment)
    db.commit()
