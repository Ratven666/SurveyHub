from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.students.group_subject import group_subject_association

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    students: Mapped[list["Student"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )

    subjects: Mapped[list["Subject"]] = relationship(
        secondary=group_subject_association,
        back_populates="groups",
    )

    teacher_assignments: Mapped[list["TeacherAssignment"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
