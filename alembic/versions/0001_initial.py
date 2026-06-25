"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-24 19:45:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # groups  (name: String(50), не 100)
    # ------------------------------------------------------------------
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ------------------------------------------------------------------
    # subjects
    # ------------------------------------------------------------------
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("training_direction", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ------------------------------------------------------------------
    # teachers  (email убран — его нет в ORM-модели)
    # ------------------------------------------------------------------
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # equipment
    # ------------------------------------------------------------------
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ------------------------------------------------------------------
    # audience_slots
    # ------------------------------------------------------------------
    op.create_table(
        "audience_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("pair_number", sa.Integer(), nullable=False),
        sa.Column("desk_capacity", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("device_capacity", sa.Integer(), nullable=False, server_default="5"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("weekday", "pair_number", name="uq_audience_slot_weekday_pair"),
        sa.CheckConstraint("weekday >= 1 AND weekday <= 5", name="ck_audience_slots_weekday"),
        sa.CheckConstraint("pair_number >= 1 AND pair_number <= 5", name="ck_audience_slots_pair_number"),
        sa.CheckConstraint("desk_capacity >= 0", name="ck_audience_slots_desk_capacity"),
        sa.CheckConstraint("device_capacity >= 0", name="ck_audience_slots_device_capacity"),
        sa.CheckConstraint(
            "desk_capacity + device_capacity > 0",
            name="ck_audience_slots_total_capacity_positive",
        ),
    )

    # ------------------------------------------------------------------
    # group_subject_association
    # ------------------------------------------------------------------
    op.create_table(
        "group_subject_association",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("group_id", "subject_id"),
    )

    # ------------------------------------------------------------------
    # students  (full_name → last_name / first_name / middle_name,
    #            добавлены student_card_number, chip_card_number)
    # ------------------------------------------------------------------
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("student_card_number", sa.String(length=50), nullable=True),
        sa.Column("chip_card_number", sa.String(length=50), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.UniqueConstraint("student_card_number", name="uq_students_student_card_number"),
        sa.UniqueConstraint("chip_card_number", name="uq_students_chip_card_number"),
    )

    # ------------------------------------------------------------------
    # lab_works  (добавлен order_number)
    # ------------------------------------------------------------------
    op.create_table(
        "lab_works",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
    )

    # ------------------------------------------------------------------
    # teacher_assignments
    # ------------------------------------------------------------------
    op.create_table(
        "teacher_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.UniqueConstraint(
            "teacher_id", "subject_id", "group_id",
            name="uq_teacher_subject_group",
        ),
    )

    # ------------------------------------------------------------------
    # equipment_units
    # ------------------------------------------------------------------
    op.create_table(
        "equipment_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="working"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.UniqueConstraint("serial_number", name="uq_equipment_units_serial_number"),
        sa.CheckConstraint(
            "status IN ('working', 'broken', 'maintenance', 'decommissioned')",
            name="ck_equipment_units_status",
        ),
    )

    # ------------------------------------------------------------------
    # audience_registrations  (seat_type nullable=True в ORM-модели,
    #                           note добавлен из роутера)
    # ------------------------------------------------------------------
    op.create_table(
        "audience_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("slot_id", sa.Integer(), nullable=False),
        sa.Column("seat_type", sa.String(length=20), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["slot_id"], ["audience_slots.id"]),
        sa.UniqueConstraint("student_id", "slot_id", name="uq_student_slot"),
        sa.CheckConstraint(
            "seat_type IN ('desk', 'device') OR seat_type IS NULL",
            name="ck_audience_registrations_seat_type",
        ),
    )

    # ------------------------------------------------------------------
    # lab_work_equipment
    # ------------------------------------------------------------------
    op.create_table(
        "lab_work_equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lab_work_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("required_units", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lab_work_id"], ["lab_works.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.UniqueConstraint("lab_work_id", "equipment_id", name="uq_lab_work_equipment"),
        sa.CheckConstraint(
            "required_units > 0",
            name="ck_lab_work_equipment_required_units",
        ),
    )

    # ------------------------------------------------------------------
    # lab_registrations
    # ------------------------------------------------------------------
    op.create_table(
        "lab_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("lab_work_id", sa.Integer(), nullable=False),
        sa.Column("audience_slot_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["lab_work_id"], ["lab_works.id"]),
        sa.ForeignKeyConstraint(["audience_slot_id"], ["audience_slots.id"]),
        sa.UniqueConstraint(
            "student_id", "lab_work_id", "audience_slot_id",
            name="uq_student_lab_work_slot",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'cancelled', 'attended')",
            name="ck_lab_registrations_status",
        ),
    )

    # ------------------------------------------------------------------
    # lab_progress  (teacher_comment → note, по ORM-модели)
    # ------------------------------------------------------------------
    op.create_table(
        "lab_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lab_registration_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lab_registration_id"], ["lab_registrations.id"]),
        sa.CheckConstraint(
            "status IN ('started', 'in_progress', 'submitted', 'reviewed', 'defended')",
            name="ck_lab_progress_status",
        ),
    )

    # ------------------------------------------------------------------
    # lab_reports  (убраны title/content/file_path/teacher_comment,
    #               добавлен comment; unique на lab_registration_id;
    #               статусы: pending/submitted/accepted/rejected)
    # ------------------------------------------------------------------
    op.create_table(
        "lab_reports",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("lab_registration_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lab_registration_id", name="uq_lab_reports_lab_registration_id"),
        sa.ForeignKeyConstraint(
            ["lab_registration_id"], ["lab_registrations.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'submitted', 'accepted', 'rejected')",
            name="ck_lab_reports_status",
        ),
    )


def downgrade() -> None:
    op.drop_table("lab_reports")
    op.drop_table("lab_progress")
    op.drop_table("lab_registrations")
    op.drop_table("lab_work_equipment")
    op.drop_table("audience_registrations")
    op.drop_table("equipment_units")
    op.drop_table("teacher_assignments")
    op.drop_table("lab_works")
    op.drop_table("students")
    op.drop_table("group_subject_association")
    op.drop_table("audience_slots")
    op.drop_table("equipment")
    op.drop_table("teachers")
    op.drop_table("subjects")
    op.drop_table("groups")
