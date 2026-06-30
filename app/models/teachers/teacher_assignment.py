from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "teacher_id", "group_id", "subject_id",
            name="uq_teacher_group_subject",
        ),
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="assignments")
    group: Mapped["Group"] = relationship(back_populates="teacher_assignments")
    subject: Mapped["Subject"] = relationship(back_populates="teacher_assignments")
