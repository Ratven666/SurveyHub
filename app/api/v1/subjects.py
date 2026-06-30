from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import Subject

router = APIRouter(prefix="/subjects", tags=["subjects"])


class SubjectCreate(BaseModel):
    name: str
    description: str | None = None
    training_direction: str | None = None


class SubjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    training_direction: str | None = None


class SubjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    training_direction: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[SubjectRead])
def list_subjects(db: DbSession):
    return db.query(Subject).all()


@router.post("/", response_model=SubjectRead, status_code=201)
def create_subject(data: SubjectCreate, db: DbSession):
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/{subject_id}", response_model=SubjectRead)
def get_subject(subject_id: int, db: DbSession):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.patch("/{subject_id}", response_model=SubjectRead)
def update_subject(subject_id: int, data: SubjectUpdate, db: DbSession):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=204)
def delete_subject(subject_id: int, db: DbSession):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
