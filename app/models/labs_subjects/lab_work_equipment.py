from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LabWorkEquipment(Base):
    """Потребность лабораторной работы в конкретном типе оборудования."""
    __tablename__ = "lab_work_equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_work_id: Mapped[int] = mapped_column(
        ForeignKey("lab_works.id", ondelete="CASCADE"), nullable=False
    )
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    required_units: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    __table_args__ = (
        CheckConstraint(
            "required_units > 0",
            name="ck_lab_work_equipment_required_units",
        ),
        UniqueConstraint(
            "lab_work_id", "equipment_id",
            name="uq_lab_work_equipment",
        ),
    )

    lab_work: Mapped["LabWork"] = relationship(back_populates="equipment_links")
    equipment: Mapped["Equipment"] = relationship(back_populates="lab_work_links")
