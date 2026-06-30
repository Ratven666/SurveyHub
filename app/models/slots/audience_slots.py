from sqlalchemy import CheckConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AudienceSlot(Base):
    __tablename__ = "audience_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    audience_number: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Номер аудитории, например '301А' или 'Б-201'",
    )
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    pair_number: Mapped[int] = mapped_column(Integer, nullable=False)
    desk_capacity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=15, server_default="15",
        comment="Количество мест за столами (без ПК)",
    )
    device_capacity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=5, server_default="5",
        comment="Количество мест с устройствами (ПК / стенды)",
    )

    __table_args__ = (
        CheckConstraint(
            "audience_number != ''",
            name="ck_audience_slots_audience_number_not_empty",
        ),
        CheckConstraint("weekday >= 1 AND weekday <= 5", name="ck_audience_slots_weekday"),
        CheckConstraint(
            "pair_number >= 1 AND pair_number <= 5",
            name="ck_audience_slots_pair_number",
        ),
        CheckConstraint("desk_capacity >= 0", name="ck_audience_slots_desk_capacity"),
        CheckConstraint("device_capacity >= 0", name="ck_audience_slots_device_capacity"),
        CheckConstraint(
            "desk_capacity + device_capacity > 0",
            name="ck_audience_slots_total_capacity_positive",
        ),
        UniqueConstraint(
            "audience_number", "weekday", "pair_number",
            name="uq_audience_slot_audience_weekday_pair",
        ),
    )

    registrations: Mapped[list["LabWorksRegistration"]] = relationship(
        back_populates="slot",
        cascade="all, delete-orphan",
    )
