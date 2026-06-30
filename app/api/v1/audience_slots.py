from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.api.deps import DbSession
from app.models import AudienceSlot

router = APIRouter(prefix="/audience-slots", tags=["audience-slots"])


class AudienceSlotCreate(BaseModel):
    audience_number: str
    weekday: int = Field(ge=1, le=5)        # 1=Пн .. 5=Пт
    pair_number: int = Field(ge=1, le=5)    # 1..5
    desk_capacity: int = Field(default=15, ge=0)
    device_capacity: int = Field(default=5, ge=0)

    @model_validator(mode="after")
    def check_total_capacity(self) -> "AudienceSlotCreate":
        if self.desk_capacity + self.device_capacity == 0:
            raise ValueError("Суммарная ёмкость (desk + device) должна быть > 0")
        return self


class AudienceSlotUpdate(BaseModel):
    audience_number: str | None = None
    weekday: int | None = Field(default=None, ge=1, le=5)
    pair_number: int | None = Field(default=None, ge=1, le=5)
    desk_capacity: int | None = Field(default=None, ge=0)
    device_capacity: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_total_capacity(self) -> "AudienceSlotUpdate":
        # Валидируем только если оба поля переданы одновременно в одном запросе.
        # Проверка с учётом текущих значений БД — в эндпоинте update_audience_slot.
        d = self.desk_capacity
        v = self.device_capacity
        if d is not None and v is not None and d + v == 0:
            raise ValueError("Суммарная ёмкость (desk + device) должна быть > 0")
        return self


class AudienceSlotRead(BaseModel):
    id: int
    audience_number: str
    weekday: int
    pair_number: int
    desk_capacity: int
    device_capacity: int

    model_config = {"from_attributes": True}


def _get_slot_or_404(slot_id: int, db: DbSession) -> AudienceSlot:
    slot = db.get(AudienceSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="AudienceSlot not found")
    return slot


@router.get("/", response_model=list[AudienceSlotRead])
def list_audience_slots(
    db: DbSession,
    audience_number: str | None = None,
    weekday: int | None = None,
    pair_number: int | None = None,
):
    q = db.query(AudienceSlot)
    if audience_number is not None:
        q = q.filter(AudienceSlot.audience_number == audience_number)
    if weekday is not None:
        q = q.filter(AudienceSlot.weekday == weekday)
    if pair_number is not None:
        q = q.filter(AudienceSlot.pair_number == pair_number)
    return q.order_by(AudienceSlot.audience_number, AudienceSlot.weekday, AudienceSlot.pair_number).all()


@router.post("/", response_model=AudienceSlotRead, status_code=201)
def create_audience_slot(data: AudienceSlotCreate, db: DbSession):
    slot = AudienceSlot(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/{slot_id}", response_model=AudienceSlotRead)
def get_audience_slot(slot_id: int, db: DbSession):
    return _get_slot_or_404(slot_id, db)


@router.patch("/{slot_id}", response_model=AudienceSlotRead)
def update_audience_slot(slot_id: int, data: AudienceSlotUpdate, db: DbSession):
    slot = _get_slot_or_404(slot_id, db)
    updates = data.model_dump(exclude_unset=True)

    # Проверяем суммарную ёмкость с учётом текущих значений в БД,
    # если изменяется хотя бы одно из двух полей ёмкости.
    if "desk_capacity" in updates or "device_capacity" in updates:
        new_desk = updates.get("desk_capacity", slot.desk_capacity)
        new_device = updates.get("device_capacity", slot.device_capacity)
        if new_desk + new_device == 0:
            raise HTTPException(
                status_code=422,
                detail="Суммарная ёмкость (desk + device) должна быть > 0",
            )

    for field, value in updates.items():
        setattr(slot, field, value)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/{slot_id}", status_code=204)
def delete_audience_slot(slot_id: int, db: DbSession):
    slot = _get_slot_or_404(slot_id, db)
    db.delete(slot)
    db.commit()
