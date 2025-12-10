"""create quotations and embeddings

Revision ID: 46bda2a5cc90
Revises: 
Create Date: 2025-12-10 16:20:08.714255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR

# revision identifiers, used by Alembic.
revision: str = '46bda2a5cc90'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create pgvector extension and core quotation tables.
    """
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "quotations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("supplier", sa.String(length=255), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("structured_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_index("ix_quotations_id", "quotations", ["id"])
    op.create_index("ix_quotations_supplier", "quotations", ["supplier"])

    op.create_table(
        "quotation_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quotation_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("embedding", VECTOR(1536), nullable=False),
        sa.ForeignKeyConstraint(
            ["quotation_id"],
            ["quotations.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_quotation_embeddings_quotation_id",
        "quotation_embeddings",
        ["quotation_id"],
    )


def downgrade() -> None:
    """
    Drop quotation tables and pgvector extension.
    """
    op.drop_index(
        "ix_quotation_embeddings_quotation_id",
        table_name="quotation_embeddings",
    )
    op.drop_table("quotation_embeddings")

    op.drop_index("ix_quotations_supplier", table_name="quotations")
    op.drop_index("ix_quotations_id", table_name="quotations")
    op.drop_table("quotations")

    op.execute("DROP EXTENSION IF EXISTS vector;")
