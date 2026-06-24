from sqlalchemy import ForeignKey, Table, Column, Integer
from app.db.base import Base

group_subject_association = Table(
    "group_subject_association",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True),
)
