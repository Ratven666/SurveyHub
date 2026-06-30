from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StudentRegistration(Base):
    """
    Участие конкретного студента в записи на лабораторную работу.
    M2M association object: Student ↔ LabWorksRegistration.
    """

    __tablename__ = "student_registrations"

    id: Mapped[int] = mapped_column(primary_key=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    lab_works_registration_id: Mapped[int] = mapped_column(
        ForeignKey("lab_works_registrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        comment="pending | confirmed | cancelled | attended | missed",
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id", "lab_works_registration_id",
            name="uq_student_lab_works_registration",
        ),
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled', 'attended', 'missed')",
            name="ck_student_registrations_status",
        ),
    )

    student: Mapped["Student"] = relationship(
        back_populates="registration_links",
    )
    lab_works_registration: Mapped["LabWorksRegistration"] = relationship(
        back_populates="student_links",
    )
