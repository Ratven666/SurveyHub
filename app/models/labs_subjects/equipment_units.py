from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EquipmentUnit(Base):
    """Конкретный физический экземпляр прибора."""
    __tablename__ = "equipment_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    # Человекочитаемое название конкретного экземпляра (например "Нивелир №3")
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True
    )
    # Инвентарный номер — опциональный, уникален если задан
    inventory_number: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="working", server_default="working"
    )


    __table_args__ = (
        CheckConstraint(
            "status IN ('working', 'repair', 'reserve', 'broken', 'decommissioned')",
            name="ck_equipment_units_status",
        ),
    )

    equipment: Mapped["Equipment"] = relationship(back_populates="units")
