"""adiciona colaboradores e vinculo com comandas

Revision ID: c3e7f4a9b821
Revises: 8a1f2c9b0d21
Create Date: 2026-08-07 13:45:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3e7f4a9b821"
down_revision: Union[str, None] = "8a1f2c9b0d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_employees_id"),
        "employees",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_employees_owner_id"),
        "employees",
        ["owner_id"],
        unique=False,
    )

    op.add_column(
        "comandas",
        sa.Column(
            "employee_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_comandas_employee_id_employees",
        "comandas",
        "employees",
        ["employee_id"],
        ["id"],
    )

    op.create_index(
        op.f("ix_comandas_employee_id"),
        "comandas",
        ["employee_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_comandas_employee_id"),
        table_name="comandas",
    )

    op.drop_constraint(
        "fk_comandas_employee_id_employees",
        "comandas",
        type_="foreignkey",
    )

    op.drop_column(
        "comandas",
        "employee_id",
    )

    op.drop_index(
        op.f("ix_employees_owner_id"),
        table_name="employees",
    )

    op.drop_index(
        op.f("ix_employees_id"),
        table_name="employees",
    )

    op.drop_table("employees")
