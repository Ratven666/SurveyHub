from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LabReport(Base):
    __tablename__ = "lab_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lab_registration_id: Mapped[int] = mapped_column(
        ForeignKey("lab_registrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'submitted', 'accepted', 'rejected')",
            name="ck_lab_reports_status",
        ),
    )

    lab_registration: Mapped["LabRegistration"] = relationship(
        "LabRegistration",
        back_populates="report",
    )
