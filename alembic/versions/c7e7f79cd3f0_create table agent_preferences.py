"""create table agent_preferences

Revision ID: c7e7f79cd3f0
Revises: 45ba7d8be2ed
Create Date: 2024-09-30 18:41:33.974136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e7f79cd3f0'
down_revision: Union[str, None] = '45ba7d8be2ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agent_preferences relational table
    op.create_table(
        'agent_preferences',
        sa.Column('agent_id', sa.Integer, sa.ForeignKey('agents.id'), primary_key=True),
        sa.Column('calendar_id', sa.String(length=255), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('agent_preferences')
