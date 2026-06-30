from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RegistrationEquipment(Base):
    """
    Конкретный физический прибор (EquipmentUnit), закреплённый
    за записью на лабораторную работу (LabWorksRegistration).
    """

    __tablename__ = "registration_equipment"

    id: Mapped[int] = mapped_column(primary_key=True)

    lab_works_registration_id: Mapped[int] = mapped_column(
        ForeignKey("lab_works_registrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    equipment_unit_id: Mapped[int] = mapped_column(
        ForeignKey("equipment_units.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Конкретный физический экземпляр прибора",
    )

    __table_args__ = (
        UniqueConstraint(
            "lab_works_registration_id",
            "equipment_unit_id",
            name="uq_registration_equipment_unit",
        ),
    )

    lab_works_registration: Mapped["LabWorksRegistration"] = relationship(
        back_populates="equipment_links",
    )
    equipment_unit: Mapped["EquipmentUnit"] = relationship(
        back_populates="registration_links",
    )
