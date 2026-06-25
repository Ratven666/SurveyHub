from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import Group, Student

router = APIRouter(prefix="/students", tags=["students"])


class StudentCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: str | None = None
    student_card_number: str | None = None
    chip_card_number: str | None = None
    group_id: int


class StudentUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    student_card_number: str | None = None
    chip_card_number: str | None = None
    group_id: int | None = None


class StudentRead(BaseModel):
    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    student_card_number: str | None
    chip_card_number: str | None
    group_id: int
    full_name: str

    model_config = {"from_attributes": True}


def _get_group_or_404(group_id: int, db: DbSession) -> Group:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail=f"Group with id={group_id} not found",
        )
    return group


@router.get("/", response_model=list[StudentRead])
def list_students(db: DbSession, group_id: int | None = None):
    q = db.query(Student)
    if group_id is not None:
        q = q.filter(Student.group_id == group_id)
    return q.all()


@router.post("/", response_model=StudentRead, status_code=201)
def create_student(data: StudentCreate, db: DbSession):
    _get_group_or_404(data.group_id, db)
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: DbSession):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(student_id: int, data: StudentUpdate, db: DbSession):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    updates = data.model_dump(exclude_unset=True)

    if "group_id" in updates:
        _get_group_or_404(updates["group_id"], db)

    for field, value in updates.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: DbSession):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
