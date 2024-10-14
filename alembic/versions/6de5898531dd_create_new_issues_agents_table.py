"""create new issues_agents table

Revision ID: 6de5898531dd
Revises: d7ba761b8b8f
Create Date: 2024-09-24 12:37:03.880496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6de5898531dd'
down_revision: Union[str, None] = 'd7ba761b8b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'created_at' and 'updated_at' columns to the 'issues' table
    op.add_column('issues', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('issues', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False))

    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('smb_id', sa.Integer, sa.ForeignKey('smbs.id')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('speciality', sa.String, nullable=False),
        sa.Column('service', sa.String, nullable=False),
        sa.Column('rating', sa.Float, nullable=False),
        sa.Column('picture', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # Create issue_agents relational table
    op.create_table(
        'issues_agents',
        sa.Column('issue_id', sa.Integer, sa.ForeignKey('issues.id'), primary_key=True),
        sa.Column('agent_id', sa.Integer, sa.ForeignKey('agents.id'), primary_key=True),
        sa.Column('status', sa.String(10), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('issues_agents')
    op.drop_table('agents')
    
    # Drop the columns in case of rollback
    op.drop_column('issues', 'created_at')
    op.drop_column('issues', 'updated_at')
