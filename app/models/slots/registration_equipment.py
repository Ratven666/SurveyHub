from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RegistrationEquipment(Base):
    """
    Конкретный физический прибор (EquipmentUnit), закреплённый
    за записью студента в аудиторию (AudienceRegistration).

    Семантика:
      - один прибор может фигурировать в разных регистрациях
        (в разные слоты / разным студентам);
      - одна регистрация может включать несколько приборов;
      - в рамках одной регистрации один и тот же экземпляр прибора
        встречается не более одного раза (UniqueConstraint).
    """

    __tablename__ = "registration_equipment"

    id: Mapped[int] = mapped_column(primary_key=True)

    audience_registration_id: Mapped[int] = mapped_column(
        ForeignKey("audience_registrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    equipment_unit_id: Mapped[int] = mapped_column(
        ForeignKey("equipment_units.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Конкретный физический экземпляр прибора",
    )

    __table_args__ = (
        UniqueConstraint(
            "audience_registration_id",
            "equipment_unit_id",
            name="uq_registration_equipment_unit",
        ),
    )

    audience_registration: Mapped["AudienceRegistration"] = relationship(
        back_populates="equipment_links",
    )
    equipment_unit: Mapped["EquipmentUnit"] = relationship(
        back_populates="registration_links",
    )
