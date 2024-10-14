"""add column password in smbs

Revision ID: c6e5fae955ee
Revises: c7e7f79cd3f0
Create Date: 2024-10-07 14:36:08.408327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6e5fae955ee'
down_revision: Union[str, None] = 'c7e7f79cd3f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('smbs', sa.Column('password', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('smbs', 'password')
