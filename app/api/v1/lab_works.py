from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, model_validator

from app.api.deps import DbSession
from app.models import LabWork

router = APIRouter(prefix="/lab-works", tags=["lab-works"])


class LabWorkCreate(BaseModel):
    title: str
    description: str | None = None
    order_number: int
    subject_id: int
    min_students: int = 1
    max_students: int = 1

    @model_validator(mode="after")
    def check_min_max(self) -> "LabWorkCreate":
        if self.min_students < 1:
            raise ValueError("min_students must be >= 1")
        if self.max_students < 1:
            raise ValueError("max_students must be >= 1")
        if self.max_students < self.min_students:
            raise ValueError("max_students must be >= min_students")
        return self


class LabWorkUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order_number: int | None = None
    subject_id: int | None = None
    min_students: int | None = None
    max_students: int | None = None

    @model_validator(mode="after")
    def check_min_max(self) -> "LabWorkUpdate":
        mn = self.min_students
        mx = self.max_students
        if mn is not None and mn < 1:
            raise ValueError("min_students must be >= 1")
        if mx is not None and mx < 1:
            raise ValueError("max_students must be >= 1")
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

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[LabWorkRead])
def list_lab_works(db: DbSession, subject_id: int | None = None):
    q = db.query(LabWork)
    if subject_id is not None:
        q = q.filter(LabWork.subject_id == subject_id)
    return q.order_by(LabWork.subject_id, LabWork.order_number).all()


@router.post("/", response_model=LabWorkRead, status_code=201)
def create_lab_work(data: LabWorkCreate, db: DbSession):
    lab_work = LabWork(**data.model_dump())
    db.add(lab_work)
    db.commit()
    db.refresh(lab_work)
    return lab_work


@router.get("/{lab_work_id}", response_model=LabWorkRead)
def get_lab_work(lab_work_id: int, db: DbSession):
    lab_work = db.get(LabWork, lab_work_id)
    if not lab_work:
        raise HTTPException(status_code=404, detail="LabWork not found")
    return lab_work


@router.patch("/{lab_work_id}", response_model=LabWorkRead)
def update_lab_work(lab_work_id: int, data: LabWorkUpdate, db: DbSession):
    lab_work = db.get(LabWork, lab_work_id)
    if not lab_work:
        raise HTTPException(status_code=404, detail="LabWork not found")

    updates = data.model_dump(exclude_unset=True)

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
    lab_work = db.get(LabWork, lab_work_id)
    if not lab_work:
        raise HTTPException(status_code=404, detail="LabWork not found")
    db.delete(lab_work)
    db.commit()
