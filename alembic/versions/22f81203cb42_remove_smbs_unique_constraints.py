"""remove smbs unique constraints

Revision ID: 22f81203cb42
Revises: c345712aff7f
Create Date: 2024-09-17 14:44:06.430674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22f81203cb42'
down_revision: Union[str, None] = 'c345712aff7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('unique_name_website', 'smbs', type_='unique')
    op.create_unique_constraint('unique_website', 'smbs', ['website'])
    op.create_unique_constraint('unique_phone_smb_id', 'visitors', ['phone', 'smb_id'])


def downgrade() -> None:
    op.create_unique_constraint('unique_name_website', 'smbs', ['name', 'website'])
    op.drop_constraint('unique_website', 'smbs', type_='unique')
    op.drop_constraint('unique_phone_smb_id', 'visitors', type_='unique')

