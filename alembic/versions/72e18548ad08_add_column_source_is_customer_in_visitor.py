"""add column source_is_customer in visitor

Revision ID: 72e18548ad08
Revises: 6de5898531dd
Create Date: 2024-09-26 12:23:54.633469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72e18548ad08'
down_revision: Union[str, None] = '6de5898531dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'source' and 'is_customer' columns to the 'visitors' table
    op.add_column('visitors', sa.Column('source', sa.String(5), server_default=sa.text("'ew'"), nullable=False)),
    op.add_column('visitors', sa.Column('is_customer', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('visitors', 'source')
    op.drop_column('visitors', 'is_customer')
