from sqlalchemy import CheckConstraint, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    lab_work_links: Mapped[list["LabWorkEquipment"]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
    )
    units: Mapped[list["EquipmentUnit"]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
    )
