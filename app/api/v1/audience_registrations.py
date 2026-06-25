from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import AudienceRegistration

router = APIRouter(prefix="/audience-registrations", tags=["audience-registrations"])

SeatType = Literal["computer", "workbench", "stand"]


class AudienceRegistrationCreate(BaseModel):
    student_id: int
    audience_slot_id: int
    seat_type: SeatType | None = None
    note: str | None = None


class AudienceRegistrationUpdate(BaseModel):
    seat_type: SeatType | None = None
    note: str | None = None


class AudienceRegistrationRead(BaseModel):
    id: int
    student_id: int
    audience_slot_id: int
    seat_type: str | None
    note: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[AudienceRegistrationRead])
def list_audience_registrations(
    db: DbSession,
    student_id: int | None = None,
    audience_slot_id: int | None = None,
    seat_type: str | None = None,
):
    q = db.query(AudienceRegistration)
    if student_id is not None:
        q = q.filter(AudienceRegistration.student_id == student_id)
    if audience_slot_id is not None:
        q = q.filter(AudienceRegistration.audience_slot_id == audience_slot_id)
    if seat_type is not None:
        q = q.filter(AudienceRegistration.seat_type == seat_type)
    return q.all()


@router.post("/", response_model=AudienceRegistrationRead, status_code=201)
def create_audience_registration(data: AudienceRegistrationCreate, db: DbSession):
    reg = AudienceRegistration(**data.model_dump())
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.get("/{reg_id}", response_model=AudienceRegistrationRead)
def get_audience_registration(reg_id: int, db: DbSession):
    reg = db.get(AudienceRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="AudienceRegistration not found")
    return reg


@router.patch("/{reg_id}", response_model=AudienceRegistrationRead)
def update_audience_registration(reg_id: int, data: AudienceRegistrationUpdate, db: DbSession):
    reg = db.get(AudienceRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="AudienceRegistration not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(reg, field, value)
    db.commit()
    db.refresh(reg)
    return reg


@router.delete("/{reg_id}", status_code=204)
def delete_audience_registration(reg_id: int, db: DbSession):
    reg = db.get(AudienceRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="AudienceRegistration not found")
    db.delete(reg)
    db.commit()
