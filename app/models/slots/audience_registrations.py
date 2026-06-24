from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class AudienceRegistration(Base):
    __tablename__ = "audience_registrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("audience_slots.id"), nullable=False)
    seat_type: Mapped[str] = mapped_column(String(20), nullable=False)  # desk | device

    __table_args__ = (
        CheckConstraint(
            "seat_type IN ('desk', 'device')",
            name="ck_audience_registrations_seat_type",
        ),
        UniqueConstraint("student_id", "slot_id", name="uq_student_slot"),
    )

    student: Mapped["Student"] = relationship(back_populates="audience_registrations")
    slot: Mapped["AudienceSlot"] = relationship(back_populates="registrations")
