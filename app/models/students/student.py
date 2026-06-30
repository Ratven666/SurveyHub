from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    student_card_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, unique=True
    )
    chip_card_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, unique=True
    )
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)

    group: Mapped["Group"] = relationship(back_populates="students")

    # Записи, которые студент создал (он — организатор)
    created_registrations: Mapped[list["LabWorksRegistration"]] = relationship(
        back_populates="creator",
        foreign_keys="LabWorksRegistration.creator_id",
    )

    # M2M — все записи на лабы, в которых студент участвует
    registration_links: Mapped[list["StudentRegistration"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )
    lab_works_registrations: Mapped[list["LabWorksRegistration"]] = relationship(
        secondary="student_registrations",
        back_populates="students",
        viewonly=True,
    )

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
