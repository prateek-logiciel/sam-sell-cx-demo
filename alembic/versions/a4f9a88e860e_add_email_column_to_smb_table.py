"""add email column to SMB table

Revision ID: a4f9a88e860e
Revises: 8efc72d5259f
Create Date: 2024-09-16 17:05:45.685390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4f9a88e860e'
down_revision: Union[str, None] = '8efc72d5259f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the email column to the SMB table
    op.add_column('smbs', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('smbs', sa.Column('phone', sa.String(length=20), nullable=True))


def downgrade():
    # Remove the email column in case of rollback
    op.drop_column('smbs', 'email')
    op.drop_column('smbs', 'phone')
