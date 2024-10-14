"""alter column calendar_settings in smb_preferences table

Revision ID: 45ba7d8be2ed
Revises: 1b12010cbf35
Create Date: 2024-09-30 15:28:38.633169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45ba7d8be2ed'
down_revision: Union[str, None] = '1b12010cbf35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'smb_preferences',
        'calendar_settings',
        type_=sa.dialects.postgresql.JSONB(),
        postgresql_using='calendar_settings::jsonb'
    )
    op.alter_column(
        'smb_preferences',
        'storage_settings',
        type_=sa.dialects.postgresql.JSONB(),
        postgresql_using='storage_settings::jsonb'
    )


def downgrade() -> None:
    op.alter_column(
        'smb_preferences',
        'calendar_settings',
        type_=sa.dialects.postgresql.JSON(),
        postgresql_using='calendar_settings::json'
    )
    op.alter_column(
        'smb_preferences',
        'storage_settings',
        type_=sa.dialects.postgresql.JSON(),
        postgresql_using='storage_settings::json'
    )
