"""Add unique constraint to smb_preferences.smb_id

Revision ID: 8efc72d5259f
Revises: f7cfa28fbaa2
Create Date: 2024-09-04 16:40:42.839754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8efc72d5259f'
down_revision: Union[str, None] = 'f7cfa28fbaa2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add unique constraint to smb_id column
    op.create_unique_constraint('unique_name_website', 'smbs', ['name', 'website'])
    op.create_unique_constraint('unique_smb_id', 'smb_preferences', ['smb_id'])


def downgrade():
    # Drop unique constraint
    op.drop_constraint('unique_name_website', 'smbs', type_='unique')
    op.drop_constraint('unique_smb_id', 'smb_preferences', type_='unique')
