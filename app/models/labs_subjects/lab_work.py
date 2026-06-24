from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class LabWork(Base):
    __tablename__ = "lab_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    subject: Mapped["Subject"] = relationship(back_populates="lab_works")

    equipment_links: Mapped[list["LabWorkEquipment"]] = relationship(
        back_populates="lab_work",
        cascade="all, delete-orphan",
    )

    registrations: Mapped[list["LabRegistration"]] = relationship(
        back_populates="lab_work",
        cascade="all, delete-orphan",
    )
