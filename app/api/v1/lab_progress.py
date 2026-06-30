from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import LabProgress

router = APIRouter(prefix="/lab-progress", tags=["lab-progress"])

ProgressStatus = Literal["started", "in_progress", "submitted", "reviewed", "defended"]


class LabProgressCreate(BaseModel):
    lab_registration_id: int
    status: ProgressStatus
    note: str | None = None


class LabProgressUpdate(BaseModel):
    status: ProgressStatus | None = None
    note: str | None = None


class LabProgressRead(BaseModel):
    id: int
    lab_registration_id: int
    status: str
    note: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[LabProgressRead])
def list_lab_progress(
    db: DbSession,
    lab_registration_id: int | None = None,
    status: str | None = None,
):
    q = db.query(LabProgress)
    if lab_registration_id is not None:
        q = q.filter(LabProgress.lab_registration_id == lab_registration_id)
    if status is not None:
        q = q.filter(LabProgress.status == status)
    return q.all()


@router.post("/", response_model=LabProgressRead, status_code=201)
def create_lab_progress(data: LabProgressCreate, db: DbSession):
    entry = LabProgress(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/{progress_id}", response_model=LabProgressRead)
def get_lab_progress(progress_id: int, db: DbSession):
    entry = db.get(LabProgress, progress_id)
    if not entry:
        raise HTTPException(status_code=404, detail="LabProgress not found")
    return entry


@router.patch("/{progress_id}", response_model=LabProgressRead)
def update_lab_progress(progress_id: int, data: LabProgressUpdate, db: DbSession):
    entry = db.get(LabProgress, progress_id)
    if not entry:
        raise HTTPException(status_code=404, detail="LabProgress not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{progress_id}", status_code=204)
def delete_lab_progress(progress_id: int, db: DbSession):
    entry = db.get(LabProgress, progress_id)
    if not entry:
        raise HTTPException(status_code=404, detail="LabProgress not found")
    db.delete(entry)
    db.commit()
