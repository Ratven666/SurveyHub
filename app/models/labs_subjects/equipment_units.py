from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class EquipmentUnit(Base):
    __tablename__ = "equipment_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id"), nullable=False
    )
    serial_number: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="working"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('working', 'broken', 'maintenance', 'decommissioned')",
            name="ck_equipment_units_status",
        ),
    )

    equipment: Mapped["Equipment"] = relationship(
        back_populates="units"
    )
