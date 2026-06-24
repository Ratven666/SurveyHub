from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.students.group_subject import group_subject_association


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_direction: Mapped[str | None] = mapped_column(String(255), nullable=True)

    groups: Mapped[list["Group"]] = relationship(
        secondary=group_subject_association,
        back_populates="subjects",
    )

    lab_works: Mapped[list["LabWork"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
    )

    teacher_assignments: Mapped[list["TeacherAssignment"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
    )
