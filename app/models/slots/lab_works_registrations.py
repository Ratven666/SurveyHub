from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LabWorksRegistration(Base):
    """
    Запись на лабораторную работу в конкретный слот аудитории.

    - creator_id  — студент, создавший запись (организатор)
    - students    — все участники включая создателя (M2M через StudentRegistration)
    """

    __tablename__ = "lab_works_registrations"

    id: Mapped[int] = mapped_column(primary_key=True)

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("audience_slots.id"), nullable=False
    )
    lab_work_id: Mapped[int] = mapped_column(
        ForeignKey("lab_works.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Лабораторная работа, на которую открыта запись",
    )
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Студент, создавший запись",
    )
    seat_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="desk | device",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        comment="pending | confirmed | cancelled | missed | violated",
    )

    __table_args__ = (
        CheckConstraint(
            "seat_type IN ('desk', 'device')",
            name="ck_lab_works_registrations_seat_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled', 'missed', 'violated')",
            name="ck_lab_works_registrations_status",
        ),
        UniqueConstraint(
            "slot_id", "lab_work_id",
            name="uq_lab_works_registration_slot_lab",
        ),
    )

    slot: Mapped["AudienceSlot"] = relationship(back_populates="registrations")
    lab_work: Mapped["LabWork"] = relationship(back_populates="lab_works_registrations")

    creator: Mapped["Student"] = relationship(
        back_populates="created_registrations",
        foreign_keys=[creator_id],
    )

    student_links: Mapped[list["StudentRegistration"]] = relationship(
        back_populates="lab_works_registration",
        cascade="all, delete-orphan",
    )
    students: Mapped[list["Student"]] = relationship(
        secondary="student_registrations",
        back_populates="lab_works_registrations",
        viewonly=True,
    )

    equipment_links: Mapped[list["RegistrationEquipment"]] = relationship(
        back_populates="lab_works_registration",
        cascade="all, delete-orphan",
    )
