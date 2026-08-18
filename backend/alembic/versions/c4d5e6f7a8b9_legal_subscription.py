"""subscription, feedback and legal acceptance schema upgrade

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a7
"""

from alembic import op
import sqlalchemy as sa

revision = "c4d5e6f7a8b9"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    # ---------------------------------------------------------
    # ASSINATURA
    # ---------------------------------------------------------
    op.add_column(
        "users",
        sa.Column(
            "subscription_status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "subscription_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "subscription_activated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_subscription_status",
        "users",
        ["subscription_status"],
    )

    # ---------------------------------------------------------
    # FEEDBACK DE ATENDIMENTO
    # ---------------------------------------------------------
    op.add_column(
        "comandas",
        sa.Column("feedback_token_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "comandas",
        sa.Column(
            "feedback_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "comandas",
        sa.Column("feedback_rating", sa.Integer(), nullable=True),
    )
    op.add_column(
        "comandas",
        sa.Column("feedback_comment", sa.Text(), nullable=True),
    )
    op.add_column(
        "comandas",
        sa.Column(
            "feedback_responded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_comandas_feedback_token_hash",
        "comandas",
        ["feedback_token_hash"],
        unique=True,
    )

    # ---------------------------------------------------------
    # LEGAL ACCEPTANCES
    #
    # A migration anterior já criou legal_acceptances usando:
    # document_type / document_version / ip_address.
    #
    # O código atual usa:
    # terms_version / privacy_version / ip.
    #
    # Portanto migramos a tabela existente em vez de recriá-la.
    # ---------------------------------------------------------

    op.add_column(
        "legal_acceptances",
        sa.Column("terms_version", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "legal_acceptances",
        sa.Column("privacy_version", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "legal_acceptances",
        sa.Column("ip", sa.String(length=64), nullable=True),
    )

    # Preserva o máximo possível dos registros anteriores.
    op.execute(
        """
        UPDATE legal_acceptances
        SET terms_version = document_version
        WHERE document_type = 'terms'
          AND terms_version IS NULL
        """
    )

    op.execute(
        """
        UPDATE legal_acceptances
        SET privacy_version = document_version
        WHERE document_type = 'privacy'
          AND privacy_version IS NULL
        """
    )

    op.execute(
        """
        UPDATE legal_acceptances
        SET ip = ip_address
        WHERE ip IS NULL
          AND ip_address IS NOT NULL
        """
    )

    # Registros antigos podem representar Termos e Política em linhas separadas.
    # Para evitar quebrar NOT NULL durante a transição, completa com a versão
    # conhecida da outra categoria quando disponível para o mesmo usuário.
    op.execute(
        """
        UPDATE legal_acceptances la
        SET terms_version = sub.document_version
        FROM legal_acceptances sub
        WHERE la.user_id = sub.user_id
          AND sub.document_type = 'terms'
          AND la.terms_version IS NULL
        """
    )

    op.execute(
        """
        UPDATE legal_acceptances la
        SET privacy_version = sub.document_version
        FROM legal_acceptances sub
        WHERE la.user_id = sub.user_id
          AND sub.document_type = 'privacy'
          AND la.privacy_version IS NULL
        """
    )

    # Remove a constraint antiga antes de remover as colunas antigas.
    op.drop_constraint(
        "uq_legal_acceptance_user_doc_version",
        "legal_acceptances",
        type_="unique",
    )

    op.drop_index(
        "ix_legal_acceptances_document_type",
        table_name="legal_acceptances",
    )

    op.drop_column("legal_acceptances", "document_type")
    op.drop_column("legal_acceptances", "document_version")
    op.drop_column("legal_acceptances", "ip_address")

    # Não forçamos NOT NULL para registros históricos incompletos.
    # Novos registros criados pela aplicação já enviam ambas as versões.


def downgrade():
    # ---------------------------------------------------------
    # LEGAL ACCEPTANCES - rollback estrutural
    # ---------------------------------------------------------
    op.add_column(
        "legal_acceptances",
        sa.Column("document_type", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "legal_acceptances",
        sa.Column("document_version", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "legal_acceptances",
        sa.Column("ip_address", sa.String(length=64), nullable=True),
    )

    op.execute(
        """
        UPDATE legal_acceptances
        SET document_type = 'terms',
            document_version = terms_version,
            ip_address = ip
        WHERE terms_version IS NOT NULL
        """
    )

    op.create_index(
        "ix_legal_acceptances_document_type",
        "legal_acceptances",
        ["document_type"],
    )

    op.create_unique_constraint(
        "uq_legal_acceptance_user_doc_version",
        "legal_acceptances",
        ["user_id", "document_type", "document_version"],
    )

    op.drop_column("legal_acceptances", "ip")
    op.drop_column("legal_acceptances", "privacy_version")
    op.drop_column("legal_acceptances", "terms_version")

    # ---------------------------------------------------------
    # FEEDBACK
    # ---------------------------------------------------------
    op.drop_index(
        "ix_comandas_feedback_token_hash",
        table_name="comandas",
    )

    op.drop_column("comandas", "feedback_responded_at")
    op.drop_column("comandas", "feedback_comment")
    op.drop_column("comandas", "feedback_rating")
    op.drop_column("comandas", "feedback_expires_at")
    op.drop_column("comandas", "feedback_token_hash")

    # ---------------------------------------------------------
    # ASSINATURA
    # ---------------------------------------------------------
    op.drop_index(
        "ix_users_subscription_status",
        table_name="users",
    )

    op.drop_column("users", "subscription_activated_at")
    op.drop_column("users", "subscription_expires_at")
    op.drop_column("users", "subscription_status")