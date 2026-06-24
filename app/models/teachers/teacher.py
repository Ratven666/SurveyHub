from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    assignments: Mapped[list["TeacherAssignment"]] = relationship(
        back_populates="teacher",
        cascade="all, delete-orphan",
    )
