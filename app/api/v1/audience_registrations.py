from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import func

from app.api.deps import DbSession
from app.models import AudienceRegistration, AudienceSlot, Student

router = APIRouter(prefix="/audience-registrations", tags=["audience-registrations"])

SeatType = Literal["desk", "device"]
RegStatus = Literal["pending", "confirmed", "cancelled", "missed", "violated"]

# Статусы, которые считаются занимающими место
OCCUPYING_STATUSES = ("pending", "confirmed")


class AudienceRegistrationCreate(BaseModel):
    student_id: int
    slot_id: int
    seat_type: SeatType
    status: RegStatus = "pending"


class AudienceRegistrationUpdate(BaseModel):
    seat_type: SeatType | None = None
    status: RegStatus | None = None


class AudienceRegistrationRead(BaseModel):
    id: int
    student_id: int
    slot_id: int
    seat_type: str
    status: str

    model_config = {"from_attributes": True}


def _get_reg_or_404(reg_id: int, db: DbSession) -> AudienceRegistration:
    reg = db.get(AudienceRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="AudienceRegistration not found")
    return reg


def _validate_fk(student_id: int, slot_id: int, db: DbSession) -> AudienceSlot:
    """Проверяет существование студента и слота, возвращает слот."""
    if not db.get(Student, student_id):
        raise HTTPException(status_code=404, detail=f"Student with id={student_id} not found")
    slot = db.get(AudienceSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail=f"AudienceSlot with id={slot_id} not found")
    return slot


def _check_seat_availability(slot: AudienceSlot, seat_type: str, db: DbSession) -> None:
    """
    Проверяет наличие свободных мест нужного типа в слоте.
    Учитываются только активные записи (pending + confirmed).
    """
    # Ёмкость из слота в зависимости от типа места
    capacity: int = slot.desk_capacity if seat_type == "desk" else slot.device_capacity

    # Количество уже занятых мест данного типа в этом слоте
    occupied: int = (
        db.query(func.count(AudienceRegistration.id))
        .filter(
            AudienceRegistration.slot_id == slot.id,
            AudienceRegistration.seat_type == seat_type,
            AudienceRegistration.status.in_(OCCUPYING_STATUSES),
        )
        .scalar()
    )

    if occupied >= capacity:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No available '{seat_type}' seats in AudienceSlot id={slot.id}: "
                f"{occupied}/{capacity} occupied"
            ),
        )


@router.get("/", response_model=list[AudienceRegistrationRead])
def list_audience_registrations(
    db: DbSession,
    student_id: int | None = None,
    slot_id: int | None = None,
    seat_type: SeatType | None = None,
    status: RegStatus | None = None,
):
    q = db.query(AudienceRegistration)
    if student_id is not None:
        q = q.filter(AudienceRegistration.student_id == student_id)
    if slot_id is not None:
        q = q.filter(AudienceRegistration.slot_id == slot_id)
    if seat_type is not None:
        q = q.filter(AudienceRegistration.seat_type == seat_type)
    if status is not None:
        q = q.filter(AudienceRegistration.status == status)
    return q.all()


@router.post("/", response_model=AudienceRegistrationRead, status_code=201)
def create_audience_registration(data: AudienceRegistrationCreate, db: DbSession):
    slot = _validate_fk(data.student_id, data.slot_id, db)

    # Проверяем вместимость только для активных статусов.
    # Если запись сразу создаётся как cancelled — она не занимает место.
    if data.status in OCCUPYING_STATUSES:
        _check_seat_availability(slot, data.seat_type, db)

    reg = AudienceRegistration(**data.model_dump())
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.get("/{reg_id}", response_model=AudienceRegistrationRead)
def get_audience_registration(reg_id: int, db: DbSession):
    return _get_reg_or_404(reg_id, db)


@router.patch("/{reg_id}", response_model=AudienceRegistrationRead)
def update_audience_registration(reg_id: int, data: AudienceRegistrationUpdate, db: DbSession):
    reg = _get_reg_or_404(reg_id, db)
    updates = data.model_dump(exclude_unset=True)

    # Если статус меняется на активный или меняется тип места при активном статусе —
    # нужно проверить вместимость. Исключаем текущую запись из подсчёта (она ещё не обновлена).
    new_status = updates.get("status", reg.status)
    new_seat_type = updates.get("seat_type", reg.seat_type)

    status_becomes_active = (
        reg.status not in OCCUPYING_STATUSES and new_status in OCCUPYING_STATUSES
    )
    seat_type_changed_while_active = (
        reg.status in OCCUPYING_STATUSES
        and new_seat_type != reg.seat_type
    )

    if status_becomes_active or seat_type_changed_while_active:
        slot = reg.slot

        # Временно считаем, что текущая запись не занимает место нового типа,
        # поэтому вычитаем её из счётчика вручную через exclude_id
        occupied: int = (
            db.query(func.count(AudienceRegistration.id))
            .filter(
                AudienceRegistration.slot_id == slot.id,
                AudienceRegistration.seat_type == new_seat_type,
                AudienceRegistration.status.in_(OCCUPYING_STATUSES),
                AudienceRegistration.id != reg.id,  # исключаем саму себя
            )
            .scalar()
        )
        capacity = slot.desk_capacity if new_seat_type == "desk" else slot.device_capacity
        if occupied >= capacity:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"No available '{new_seat_type}' seats in AudienceSlot id={slot.id}: "
                    f"{occupied}/{capacity} occupied"
                ),
            )

    for field, value in updates.items():
        setattr(reg, field, value)
    db.commit()
    db.refresh(reg)
    return reg


@router.delete("/{reg_id}", status_code=204)
def delete_audience_registration(reg_id: int, db: DbSession):
    reg = _get_reg_or_404(reg_id, db)
    db.delete(reg)
    db.commit()
