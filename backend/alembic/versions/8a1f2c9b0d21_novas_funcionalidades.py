"""novas funcionalidades: servicos catalogados, agenda, marketing, config usuario

Revision ID: 8a1f2c9b0d21
Revises: 5de784d02b98
Create Date: 2026-08-06 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "8a1f2c9b0d21"
down_revision: Union[str, None] = "5de784d02b98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # =====================================================
    # USERS
    # =====================================================

    user_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "phone" not in user_columns:
        op.add_column(
            "users",
            sa.Column(
                "phone",
                sa.String(length=20),
                nullable=True
            )
        )

    if "theme" not in user_columns:
        op.add_column(
            "users",
            sa.Column(
                "theme",
                sa.String(length=10),
                nullable=True,
                server_default="escuro"
            )
        )


    # =====================================================
    # TABELAS EXISTENTES
    # =====================================================

    table_names = set(inspector.get_table_names())


    # =====================================================
    # APPOINTMENTS
    # =====================================================

    if "appointments" not in table_names:

        op.create_table(
            "appointments",

            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True
            ),

            sa.Column(
                "client_id",
                sa.Integer(),
                sa.ForeignKey("clients.id"),
                nullable=False
            ),

            sa.Column(
                "service_id",
                sa.Integer(),
                sa.ForeignKey("services.id"),
                nullable=True
            ),

            sa.Column(
                "scheduled_at",
                sa.DateTime(timezone=True),
                nullable=False
            ),

            sa.Column(
                "reminder_minutes_before",
                sa.Integer(),
                server_default="60"
            ),

            sa.Column(
                "notes",
                sa.Text(),
                nullable=True
            ),

            sa.Column(
                "status",
                sa.String(length=20),
                server_default="agendado"
            ),

            sa.Column(
                "notified",
                sa.Boolean(),
                server_default=sa.false()
            ),

            sa.Column(
                "owner_id",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False
            ),

            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now()
            )
        )

        op.create_index(
            "ix_appointments_client_id",
            "appointments",
            ["client_id"]
        )

        op.create_index(
            "ix_appointments_owner_id",
            "appointments",
            ["owner_id"]
        )

        op.create_index(
            "ix_appointments_scheduled_at",
            "appointments",
            ["scheduled_at"]
        )


    # =====================================================
    # CAMPAIGNS
    # =====================================================

    if "campaigns" not in table_names:

        op.create_table(
            "campaigns",

            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True
            ),

            sa.Column(
                "channel",
                sa.String(length=10),
                nullable=False
            ),

            sa.Column(
                "subject",
                sa.String(length=200),
                nullable=True
            ),

            sa.Column(
                "message",
                sa.Text(),
                nullable=False
            ),

            sa.Column(
                "total_destinatarios",
                sa.Integer(),
                server_default="0"
            ),

            sa.Column(
                "total_enviados",
                sa.Integer(),
                server_default="0"
            ),

            sa.Column(
                "total_falhas",
                sa.Integer(),
                server_default="0"
            ),

            sa.Column(
                "owner_id",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False
            ),

            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now()
            )
        )

        op.create_index(
            "ix_campaigns_owner_id",
            "campaigns",
            ["owner_id"]
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    table_names = set(inspector.get_table_names())

    if "campaigns" in table_names:
        op.drop_table("campaigns")

    if "appointments" in table_names:
        op.drop_table("appointments")

    user_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "theme" in user_columns:
        op.drop_column("users", "theme")

    if "phone" in user_columns:
        op.drop_column("users", "phone")