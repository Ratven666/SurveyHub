from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import LabRegistration

router = APIRouter(prefix="/lab-registrations", tags=["lab-registrations"])

LabRegStatus = Literal["pending", "approved", "cancelled", "attended"]


class LabRegistrationCreate(BaseModel):
    student_id: int
    lab_work_id: int
    audience_slot_id: int
    status: LabRegStatus = "pending"
    note: str | None = None


class LabRegistrationUpdate(BaseModel):
    status: LabRegStatus | None = None
    note: str | None = None


class LabRegistrationRead(BaseModel):
    id: int
    student_id: int
    lab_work_id: int
    audience_slot_id: int
    status: str
    note: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[LabRegistrationRead])
def list_lab_registrations(
    db: DbSession,
    student_id: int | None = None,
    lab_work_id: int | None = None,
    audience_slot_id: int | None = None,
    status: str | None = None,
):
    q = db.query(LabRegistration)
    if student_id is not None:
        q = q.filter(LabRegistration.student_id == student_id)
    if lab_work_id is not None:
        q = q.filter(LabRegistration.lab_work_id == lab_work_id)
    if audience_slot_id is not None:
        q = q.filter(LabRegistration.audience_slot_id == audience_slot_id)
    if status is not None:
        q = q.filter(LabRegistration.status == status)
    return q.all()


@router.post("/", response_model=LabRegistrationRead, status_code=201)
def create_lab_registration(data: LabRegistrationCreate, db: DbSession):
    reg = LabRegistration(**data.model_dump())
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.get("/{reg_id}", response_model=LabRegistrationRead)
def get_lab_registration(reg_id: int, db: DbSession):
    reg = db.get(LabRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="LabRegistration not found")
    return reg


@router.patch("/{reg_id}", response_model=LabRegistrationRead)
def update_lab_registration(reg_id: int, data: LabRegistrationUpdate, db: DbSession):
    reg = db.get(LabRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="LabRegistration not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(reg, field, value)
    db.commit()
    db.refresh(reg)
    return reg


@router.delete("/{reg_id}", status_code=204)
def delete_lab_registration(reg_id: int, db: DbSession):
    reg = db.get(LabRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="LabRegistration not found")
    db.delete(reg)
    db.commit()
