# alembic/versions/0001_initial.py

"""initial: full schema from scratch

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ── 1. groups ─────────────────────────────────────────────────────────────
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_groups_name"),
    )

    # ── 2. subjects ───────────────────────────────────────────────────────────
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("training_direction", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "name", "description", "training_direction",
            name="uq_subject_name_description_direction",
        ),
    )

    # ── 3. teachers ───────────────────────────────────────────────────────────
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_name", sa.String(150), nullable=False),
        sa.Column("first_name", sa.String(150), nullable=False),
        sa.Column("middle_name", sa.String(150), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("position", sa.String(255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "last_name", "first_name", "middle_name",
            "email", "department", "position",
            name="uq_teacher_name_email_department_position",
        ),
    )

    # ── 4. equipment ──────────────────────────────────────────────────────────
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_equipment_name"),
    )

    # ── 5. students ───────────────────────────────────────────────────────────
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("middle_name", sa.String(100), nullable=True),
        sa.Column("student_card_number", sa.String(50), nullable=True),
        sa.Column("chip_card_number", sa.String(50), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_card_number",
            name="uq_students_student_card_number",
        ),
        sa.UniqueConstraint(
            "chip_card_number",
            name="uq_students_chip_card_number",
        ),
    )

    # ── 6. group_subject_association (M2M) ────────────────────────────────────
    op.create_table(
        "group_subject_association",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("group_id", "subject_id"),
    )

    # ── 7. teacher_assignments ────────────────────────────────────────────────
    op.create_table(
        "teacher_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "teacher_id", "group_id", "subject_id",
            name="uq_teacher_group_subject",
        ),
    )

    # ── 8. lab_works ──────────────────────────────────────────────────────────
    op.create_table(
        "lab_works",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column(
            "required_seat_type", sa.String(20),
            nullable=False, server_default="desk",
            comment="Тип места для выполнения работы: desk | device",
        ),
        sa.Column("min_students", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_students", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "hours_to_complete", sa.Integer(),
            nullable=False, server_default="2",
            comment="Количество часов на выполнение лабораторной работы",
        ),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "required_seat_type IN ('desk', 'device')",
            name="ck_lab_works_required_seat_type",
        ),
        sa.CheckConstraint(
            "min_students >= 1",
            name="ck_lab_works_min_students_positive",
        ),
        sa.CheckConstraint(
            "max_students >= 1",
            name="ck_lab_works_max_students_positive",
        ),
        sa.CheckConstraint(
            "max_students >= min_students",
            name="ck_lab_works_max_gte_min",
        ),
        sa.CheckConstraint(
            "hours_to_complete >= 1",
            name="ck_lab_works_hours_positive",
        ),
        sa.UniqueConstraint(
            "subject_id", "order_number",
            name="uq_lab_work_subject_order",
        ),
    )

    # ── 9. equipment_units ────────────────────────────────────────────────────
    op.create_table(
        "equipment_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("inventory_number", sa.String(100), nullable=True),
        sa.Column(
            "status", sa.String(20),
            nullable=False, server_default="working",
        ),
        sa.ForeignKeyConstraint(
            ["equipment_id"], ["equipment.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "serial_number",
            name="uq_equipment_units_serial_number",
        ),
        sa.UniqueConstraint(
            "inventory_number",
            name="uq_equipment_units_inventory_number",
        ),
        sa.CheckConstraint(
            "status IN ('working', 'repair', 'reserve', 'broken', 'decommissioned')",
            name="ck_equipment_units_status",
        ),
    )

    # ── 10. lab_work_equipment ────────────────────────────────────────────────
    op.create_table(
        "lab_work_equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lab_work_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("required_units", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(
            ["lab_work_id"], ["lab_works.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["equipment_id"], ["equipment.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "required_units > 0",
            name="ck_lab_work_equipment_required_units",
        ),
        sa.UniqueConstraint(
            "lab_work_id", "equipment_id",
            name="uq_lab_work_equipment",
        ),
    )

    # ── 11. audience_slots ────────────────────────────────────────────────────
    op.create_table(
        "audience_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "audience_number", sa.String(20),
            nullable=False,
            comment="Номер аудитории, например '301А' или 'Б-201'",
        ),
        sa.Column("weekday", sa.Integer(), nullable=False),      # 1=Пн .. 5=Пт
        sa.Column("pair_number", sa.Integer(), nullable=False),  # 1..5
        sa.Column(
            "desk_capacity", sa.Integer(),
            nullable=False, server_default="15",
            comment="Количество мест за столами (без ПК)",
        ),
        sa.Column(
            "device_capacity", sa.Integer(),
            nullable=False, server_default="5",
            comment="Количество мест с устройствами (ПК / стенды)",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "audience_number != ''",
            name="ck_audience_slots_audience_number_not_empty",
        ),
        sa.CheckConstraint(
            "weekday >= 1 AND weekday <= 5",
            name="ck_audience_slots_weekday",
        ),
        sa.CheckConstraint(
            "pair_number >= 1 AND pair_number <= 5",
            name="ck_audience_slots_pair_number",
        ),
        sa.CheckConstraint(
            "desk_capacity >= 0",
            name="ck_audience_slots_desk_capacity",
        ),
        sa.CheckConstraint(
            "device_capacity >= 0",
            name="ck_audience_slots_device_capacity",
        ),
        sa.CheckConstraint(
            "desk_capacity + device_capacity > 0",
            name="ck_audience_slots_total_capacity_positive",
        ),
        sa.UniqueConstraint(
            "audience_number", "weekday", "pair_number",
            name="uq_audience_slot_audience_weekday_pair",
        ),
    )

    # ── 12. audience_registrations ────────────────────────────────────────────
    op.create_table(
        "audience_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("slot_id", sa.Integer(), nullable=False),
        sa.Column("seat_type", sa.String(20), nullable=False),
        sa.Column(
            "status", sa.String(20),
            nullable=False, server_default="pending",
            comment="Статус записи студента в аудиторию",
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["slot_id"], ["audience_slots.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "seat_type IN ('desk', 'device')",
            name="ck_audience_registrations_seat_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled', 'missed', 'violated')",
            name="ck_audience_registrations_status",
        ),
        sa.UniqueConstraint("student_id", "slot_id", name="uq_student_slot"),
    )

    # ── 13. lab_registrations ─────────────────────────────────────────────────
    op.create_table(
        "lab_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("lab_work_id", sa.Integer(), nullable=False),
        sa.Column("audience_slot_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["lab_work_id"], ["lab_works.id"]),
        sa.ForeignKeyConstraint(["audience_slot_id"], ["audience_slots.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'cancelled', 'attended')",
            name="ck_lab_registrations_status",
        ),
        sa.UniqueConstraint(
            "student_id", "lab_work_id", "audience_slot_id",
            name="uq_student_lab_work_slot",
        ),
    )

    # ── 14. lab_progress ──────────────────────────────────────────────────────
    op.create_table(
        "lab_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lab_registration_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["lab_registration_id"], ["lab_registrations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('started', 'in_progress', 'submitted', 'reviewed', 'defended')",
            name="ck_lab_progress_status",
        ),
    )

    # ── 15. lab_reports ───────────────────────────────────────────────────────
    op.create_table(
        "lab_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("lab_registration_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["lab_registration_id"], ["lab_registrations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "lab_registration_id",
            name="uq_lab_reports_lab_registration_id",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'submitted', 'accepted', 'rejected')",
            name="ck_lab_reports_status",
        ),
    )


def downgrade() -> None:
    # Удаляем строго в обратном порядке — зависимые таблицы первыми
    op.drop_table("lab_reports")
    op.drop_table("lab_progress")
    op.drop_table("lab_registrations")
    op.drop_table("audience_registrations")
    op.drop_table("audience_slots")
    op.drop_table("lab_work_equipment")
    op.drop_table("equipment_units")
    op.drop_table("lab_works")
    op.drop_table("teacher_assignments")
    op.drop_table("group_subject_association")
    op.drop_table("students")
    op.drop_table("equipment")
    op.drop_table("teachers")
    op.drop_table("subjects")
    op.drop_table("groups")