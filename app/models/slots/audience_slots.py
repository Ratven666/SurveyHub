from sqlalchemy import CheckConstraint, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class AudienceSlot(Base):
    __tablename__ = "audience_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)       # 1..5
    pair_number: Mapped[int] = mapped_column(Integer, nullable=False)   # 1..5
    desk_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    device_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    __table_args__ = (
        CheckConstraint("weekday >= 1 AND weekday <= 5", name="ck_audience_slots_weekday"),
        CheckConstraint("pair_number >= 1 AND pair_number <= 5", name="ck_audience_slots_pair_number"),
        CheckConstraint("desk_capacity >= 0", name="ck_audience_slots_desk_capacity"),
        CheckConstraint("device_capacity >= 0", name="ck_audience_slots_device_capacity"),
        CheckConstraint(
            "desk_capacity + device_capacity > 0",
            name="ck_audience_slots_total_capacity_positive",
        ),
        UniqueConstraint("weekday", "pair_number", name="uq_audience_slot_weekday_pair"),
    )

    registrations: Mapped[list["AudienceRegistration"]] = relationship(
        back_populates="slot",
        cascade="all, delete-orphan",
    )

    lab_registrations: Mapped[list["LabRegistration"]] = relationship(
        back_populates="audience_slot",
        cascade="all, delete-orphan",
    )
