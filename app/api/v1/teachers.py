from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.api.deps import DbSession
from app.models import Teacher

router = APIRouter(prefix="/teachers", tags=["teachers"])


class TeacherCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    position: str | None = None
    note: str | None = None


class TeacherUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    position: str | None = None
    note: str | None = None


class TeacherRead(BaseModel):
    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    email: str | None
    department: str | None
    position: str | None
    note: str | None
    full_name: str  # @property из модели

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TeacherRead])
def list_teachers(
    db: DbSession,
    department: str | None = None,
    position: str | None = None,
):
    q = db.query(Teacher)
    if department is not None:
        q = q.filter(Teacher.department == department)
    if position is not None:
        q = q.filter(Teacher.position == position)
    return q.order_by(Teacher.last_name, Teacher.first_name).all()


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
