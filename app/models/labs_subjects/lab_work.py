from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LabWork(Base):
    __tablename__ = "lab_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    min_students: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    max_students: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    __table_args__ = (
        CheckConstraint("min_students >= 1", name="ck_lab_works_min_students_positive"),
        CheckConstraint("max_students >= 1", name="ck_lab_works_max_students_positive"),
        CheckConstraint("max_students >= min_students", name="ck_lab_works_max_gte_min"),
    )

    subject: Mapped["Subject"] = relationship(back_populates="lab_works")

    equipment_links: Mapped[list["LabWorkEquipment"]] = relationship(
        back_populates="lab_work",
        cascade="all, delete-orphan",
    )

    registrations: Mapped[list["LabRegistration"]] = relationship(
        back_populates="lab_work",
        cascade="all, delete-orphan",
    )
