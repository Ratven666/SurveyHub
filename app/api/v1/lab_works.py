from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.api.deps import DbSession
from app.models import LabWork, Subject

router = APIRouter(prefix="/lab-works", tags=["lab-works"])


class LabWorkCreate(BaseModel):
    title: str
    description: str | None = None
    order_number: int = Field(ge=1)
    subject_id: int
    min_students: int = Field(default=1, ge=1)
    max_students: int = Field(default=1, ge=1)
    hours_to_complete: int = Field(default=2, ge=1)

    @model_validator(mode="after")
    def check_min_max(self) -> "LabWorkCreate":
        if self.max_students < self.min_students:
            raise ValueError("max_students must be >= min_students")
        return self


class LabWorkUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order_number: int | None = Field(default=None, ge=1)
    subject_id: int | None = None
    min_students: int | None = Field(default=None, ge=1)
    max_students: int | None = Field(default=None, ge=1)
    hours_to_complete: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def check_min_max(self) -> "LabWorkUpdate":
        mn = self.min_students
        mx = self.max_students
        if mn is not None and mx is not None and mx < mn:
            raise ValueError("max_students must be >= min_students")
        return self


class LabWorkRead(BaseModel):
    id: int
    title: str
    description: str | None
    order_number: int
    subject_id: int
    min_students: int
    max_students: int
    hours_to_complete: int

    model_config = {"from_attributes": True}


def _get_lab_work_or_404(lab_work_id: int, db: DbSession) -> LabWork:
    lab_work = db.get(LabWork, lab_work_id)
    if not lab_work:
        raise HTTPException(status_code=404, detail="LabWork not found")
    return lab_work


def _check_subject_exists(subject_id: int, db: DbSession) -> None:
    if not db.get(Subject, subject_id):
        raise HTTPException(status_code=404, detail=f"Subject {subject_id} not found")


@router.get("/", response_model=list[LabWorkRead])
def list_lab_works(db: DbSession, subject_id: int | None = None):
    q = db.query(LabWork)
    if subject_id is not None:
        _check_subject_exists(subject_id, db)
        q = q.filter(LabWork.subject_id == subject_id)
    return q.order_by(LabWork.subject_id, LabWork.order_number).all()


@router.post("/", response_model=LabWorkRead, status_code=201)
def create_lab_work(data: LabWorkCreate, db: DbSession):
    _check_subject_exists(data.subject_id, db)
    lab_work = LabWork(**data.model_dump())
    db.add(lab_work)
    db.commit()
    db.refresh(lab_work)
    return lab_work


@router.get("/{lab_work_id}", response_model=LabWorkRead)
def get_lab_work(lab_work_id: int, db: DbSession):
    return _get_lab_work_or_404(lab_work_id, db)


@router.patch("/{lab_work_id}", response_model=LabWorkRead)
def update_lab_work(lab_work_id: int, data: LabWorkUpdate, db: DbSession):
    lab_work = _get_lab_work_or_404(lab_work_id, db)
    updates = data.model_dump(exclude_unset=True)

    # Проверка существования нового предмета если subject_id меняется
    if "subject_id" in updates:
        _check_subject_exists(updates["subject_id"], db)

    # Проверяем min/max с учётом текущих значений в БД
    new_min = updates.get("min_students", lab_work.min_students)
    new_max = updates.get("max_students", lab_work.max_students)
    if new_max < new_min:
        raise HTTPException(
            status_code=422,
            detail=f"max_students ({new_max}) must be >= min_students ({new_min})",
        )

    for field, value in updates.items():
        setattr(lab_work, field, value)
    db.commit()
    db.refresh(lab_work)
    return lab_work


@router.delete("/{lab_work_id}", status_code=204)
def delete_lab_work(lab_work_id: int, db: DbSession):
    lab_work = _get_lab_work_or_404(lab_work_id, db)
    db.delete(lab_work)
    db.commit()
