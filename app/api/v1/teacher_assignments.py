from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import TeacherAssignment

router = APIRouter(prefix="/teacher-assignments", tags=["teacher-assignments"])


class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    group_id: int
    subject_id: int


class TeacherAssignmentRead(BaseModel):
    id: int
    teacher_id: int
    group_id: int
    subject_id: int

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TeacherAssignmentRead])
def list_assignments(
    db: DbSession,
    teacher_id: int | None = None,
    group_id: int | None = None,
    subject_id: int | None = None,
):
    q = db.query(TeacherAssignment)
    if teacher_id is not None:
        q = q.filter(TeacherAssignment.teacher_id == teacher_id)
    if group_id is not None:
        q = q.filter(TeacherAssignment.group_id == group_id)
    if subject_id is not None:
        q = q.filter(TeacherAssignment.subject_id == subject_id)
    return q.all()


@router.post("/", response_model=TeacherAssignmentRead, status_code=201)
def create_assignment(data: TeacherAssignmentCreate, db: DbSession):
    assignment = TeacherAssignment(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/{assignment_id}", response_model=TeacherAssignmentRead)
def get_assignment(assignment_id: int, db: DbSession):
    assignment = db.get(TeacherAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.delete("/{assignment_id}", status_code=204)
def delete_assignment(assignment_id: int, db: DbSession):
    assignment = db.get(TeacherAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
