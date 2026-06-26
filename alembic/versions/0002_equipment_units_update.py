"""equipment_units: add name, inventory_number, update status values

Revision ID: 0002_equipment_units_update
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_equipment_units_update"
down_revision = "0001_initial"


def upgrade():
    # Шаг 1: добавляем колонки
    with op.batch_alter_table("equipment_units", schema=None) as batch_op:
        batch_op.add_column(sa.Column("name", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("inventory_number", sa.String(100), nullable=True))

    # Шаг 2: добавляем constraint'ы и меняем CHECK статуса
    with op.batch_alter_table("equipment_units", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_equipment_units_inventory_number", ["inventory_number"]
        )
        batch_op.create_check_constraint(
            "ck_equipment_units_status",
            "status IN ('working', 'repair', 'reserve', 'broken', 'decommissioned')",
        )


def downgrade():
    with op.batch_alter_table("equipment_units", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_equipment_units_inventory_number", type_="unique"
        )
        batch_op.drop_column("inventory_number")
        batch_op.drop_column("name")