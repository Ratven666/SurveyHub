from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LabWork(Base):
    __tablename__ = "lab_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    required_seat_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="desk",
        server_default="desk",
        comment="Тип места, необходимого для выполнения работы: desk (стол) | device (ПК/стенд)",
    )

    min_students: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1",
    )
    max_students: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1",
    )
    hours_to_complete: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2, server_default="2",
        comment="Количество часов, отведённых на выполнение лабораторной работы",
    )

    __table_args__ = (
        CheckConstraint(
            "required_seat_type IN ('desk', 'device')",
            name="ck_lab_works_required_seat_type",
        ),
        CheckConstraint("min_students >= 1", name="ck_lab_works_min_students_positive"),
        CheckConstraint("max_students >= 1", name="ck_lab_works_max_students_positive"),
        CheckConstraint("max_students >= min_students", name="ck_lab_works_max_gte_min"),
        CheckConstraint("hours_to_complete >= 1", name="ck_lab_works_hours_positive"),
        UniqueConstraint("subject_id", "order_number", name="uq_lab_work_subject_order"),
    )

    subject: Mapped["Subject"] = relationship(back_populates="lab_works")

    equipment_links: Mapped[list["LabWorkEquipment"]] = relationship(
        back_populates="lab_work",
        cascade="all, delete-orphan",
    )

    lab_works_registrations: Mapped[list["LabWorksRegistration"]] = relationship(
        back_populates="lab_work",
        cascade="all, delete-orphan",
    )