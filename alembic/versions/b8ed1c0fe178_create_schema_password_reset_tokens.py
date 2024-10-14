"""create schema password_reset_tokens

Revision ID: b8ed1c0fe178
Revises: c6e5fae955ee
Create Date: 2024-10-10 16:57:01.343581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8ed1c0fe178'
down_revision: Union[str, None] = 'c6e5fae955ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expiration_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

def downgrade():
    op.drop_table('password_reset_tokens')