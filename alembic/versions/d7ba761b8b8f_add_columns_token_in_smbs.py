"""add columns token in smbs

Revision ID: d7ba761b8b8f
Revises: 22f81203cb42
Create Date: 2024-09-20 19:36:11.750630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7ba761b8b8f'
down_revision: Union[str, None] = '22f81203cb42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('smbs', sa.Column('refresh_token', sa.String(length=512), nullable=True))
    op.add_column('smbs', sa.Column('access_token', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('smbs', 'refresh_token')
    op.drop_column('smbs', 'access_token')
