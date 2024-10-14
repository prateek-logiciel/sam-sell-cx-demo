"""Initial migration to create models

Revision ID: a22d01818916
Revises: 
Create Date: 2024-08-29 18:39:41.209461
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a22d01818916'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create 'smbs' table
    op.create_table(
        'smbs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('website', sa.String(255)),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
        sa.CheckConstraint('status IN (\'active\', \'inactive\')', name='check_status'),
    )

    # Create 'smb_preferences' table
    op.create_table(
        'smb_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('smb_id', sa.Integer(), sa.ForeignKey('smbs.id'), nullable=False),
        sa.Column('calendar_settings', sa.JSON, nullable=True),
        sa.Column('storage_settings', sa.JSON, nullable=True),
    )

    # Create 'visitors' table
    op.create_table(
        'visitors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('smb_id', sa.Integer(), sa.ForeignKey('smbs.id')),
        sa.Column('name', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('location', sa.String(255)),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('browser_info', sa.JSON),
        sa.Column('created_at', sa.TIMESTAMP, default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
        sa.CheckConstraint('status IN (\'active\', \'inactive\')', name='check_status'),
    )

    # Create 'issues' table
    op.create_table(
        'issues',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('type', sa.String(10)),
        sa.Column('description', sa.String(240)),
        sa.Column('status', sa.String(10), default='OPEN'),
        sa.Column('fk_visitor_id', sa.Integer(), sa.ForeignKey('visitors.id')),
        sa.Column('fk_smb_id', sa.Integer(), sa.ForeignKey('smbs.id')),
    )

def downgrade() -> None:
    op.drop_table('smb_preferences')
    op.drop_table('smbs')
    op.drop_table('visitors')
    op.drop_table('issues')
