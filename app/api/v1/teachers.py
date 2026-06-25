from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import Teacher

router = APIRouter(prefix="/teachers", tags=["teachers"])


class TeacherCreate(BaseModel):
    full_name: str


class TeacherUpdate(BaseModel):
    full_name: str | None = None


class TeacherRead(BaseModel):
    id: int
    full_name: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TeacherRead])
def list_teachers(db: DbSession):
    return db.query(Teacher).all()


@router.post("/", response_model=TeacherRead, status_code=201)
def create_teacher(data: TeacherCreate, db: DbSession):
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(teacher_id: int, db: DbSession):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.patch("/{teacher_id}", response_model=TeacherRead)
def update_teacher(teacher_id: int, data: TeacherUpdate, db: DbSession):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(teacher_id: int, db: DbSession):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
