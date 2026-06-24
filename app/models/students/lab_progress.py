from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class LabProgress(Base):
    __tablename__ = "lab_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_registration_id: Mapped[int] = mapped_column(
        ForeignKey("lab_registrations.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('started', 'in_progress', 'submitted', 'reviewed', 'defended')",
            name="ck_lab_progress_status",
        ),
    )

    lab_registration: Mapped["LabRegistration"] = relationship(
        back_populates="progress_entries"
    )
