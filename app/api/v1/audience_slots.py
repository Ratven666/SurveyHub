from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import AudienceSlot

router = APIRouter(prefix="/audience-slots", tags=["audience-slots"])


class AudienceSlotCreate(BaseModel):
    weekday: int  # 0=Пн .. 6=Вс
    pair_number: int
    audience_id: int
    teacher_assignment_id: int


class AudienceSlotUpdate(BaseModel):
    weekday: int | None = None
    pair_number: int | None = None
    audience_id: int | None = None
    teacher_assignment_id: int | None = None


class AudienceSlotRead(BaseModel):
    id: int
    weekday: int
    pair_number: int
    audience_id: int
    teacher_assignment_id: int

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[AudienceSlotRead])
def list_audience_slots(
    db: DbSession,
    weekday: int | None = None,
    pair_number: int | None = None,
    audience_id: int | None = None,
):
    q = db.query(AudienceSlot)
    if weekday is not None:
        q = q.filter(AudienceSlot.weekday == weekday)
    if pair_number is not None:
        q = q.filter(AudienceSlot.pair_number == pair_number)
    if audience_id is not None:
        q = q.filter(AudienceSlot.audience_id == audience_id)
    return q.all()


@router.post("/", response_model=AudienceSlotRead, status_code=201)
def create_audience_slot(data: AudienceSlotCreate, db: DbSession):
    slot = AudienceSlot(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/{slot_id}", response_model=AudienceSlotRead)
def get_audience_slot(slot_id: int, db: DbSession):
    slot = db.get(AudienceSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="AudienceSlot not found")
    return slot


@router.patch("/{slot_id}", response_model=AudienceSlotRead)
def update_audience_slot(slot_id: int, data: AudienceSlotUpdate, db: DbSession):
    slot = db.get(AudienceSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="AudienceSlot not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(slot, field, value)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/{slot_id}", status_code=204)
def delete_audience_slot(slot_id: int, db: DbSession):
    slot = db.get(AudienceSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="AudienceSlot not found")
    db.delete(slot)
    db.commit()
