from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class LabRegistration(Base):
    __tablename__ = "lab_registrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    lab_work_id: Mapped[int] = mapped_column(ForeignKey("lab_works.id"), nullable=False)
    audience_slot_id: Mapped[int] = mapped_column(
        ForeignKey("audience_slots.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'cancelled', 'attended')",
            name="ck_lab_registrations_status",
        ),
        UniqueConstraint(
            "student_id",
            "lab_work_id",
            "audience_slot_id",
            name="uq_student_lab_work_slot",
        ),
    )

    student: Mapped["Student"] = relationship(back_populates="lab_registrations")
    lab_work: Mapped["LabWork"] = relationship(back_populates="registrations")
    audience_slot: Mapped["AudienceSlot"] = relationship(back_populates="lab_registrations")

    report_status: Mapped["LabReportStatus | None"] = relationship(
        back_populates="lab_registration",
        cascade="all, delete-orphan",
        uselist=False,
    )

    progress_entries: Mapped[list["LabProgress"]] = relationship(
        back_populates="lab_registration",
        cascade="all, delete-orphan",
    )