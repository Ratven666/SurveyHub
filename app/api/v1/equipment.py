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


def _get_or_404(eq_id: int, db: DbSession) -> Equipment:
    obj = db.get(Equipment, eq_id)
    if not obj:
        raise HTTPException(404, "Equipment not found")
    return obj


@router.get("/", response_model=list[EquipmentRead])
def list_equipment(db: DbSession):
    return db.query(Equipment).order_by(Equipment.name).all()


@router.post("/", response_model=EquipmentRead, status_code=201)
def create_equipment(data: EquipmentCreate, db: DbSession):
    obj = Equipment(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.get("/{eq_id}", response_model=EquipmentRead)
def get_equipment(eq_id: int, db: DbSession):
    return _get_or_404(eq_id, db)


@router.patch("/{eq_id}", response_model=EquipmentRead)
def update_equipment(eq_id: int, data: EquipmentUpdate, db: DbSession):
    obj = _get_or_404(eq_id, db)
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    db.commit(); db.refresh(obj)
    return obj


@router.delete("/{eq_id}", status_code=204)
def delete_equipment(eq_id: int, db: DbSession):
    db.delete(_get_or_404(eq_id, db)); db.commit()
