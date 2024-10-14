"""add columns in visitor

Revision ID: f7cfa28fbaa2
Revises: 193d4e77661f
Create Date: 2024-09-02 16:43:57.478953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7cfa28fbaa2'
down_revision: Union[str, None] = '193d4e77661f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('visitors', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('visitors', sa.Column('is_phone_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('visitors', sa.Column('phone', sa.String(length=20), nullable=True))

def downgrade() -> None:
    op.drop_column('visitors', 'phone')
    op.drop_column('visitors', 'is_phone_verified')
    op.drop_column('visitors', 'is_email_verified')
