"""create table appointment

Revision ID: 1b12010cbf35
Revises: 72e18548ad08
Create Date: 2024-09-26 18:09:13.163272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1b12010cbf35'
down_revision: Union[str, None] = '72e18548ad08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('smb_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('calendar', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('start_time', sa.TIMESTAMP(), nullable=False),
        sa.Column('end_time', sa.TIMESTAMP(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('attendees', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_check_constraint(
        'check_calendar_json',
        'appointments',
        "(calendar ? 'source') AND (calendar ? 'id') AND (calendar ? 'event')"
    )

    op.create_index('idx_appointments_smb_id', 'appointments', ['smb_id'])
    op.create_index('idx_appointments_agent_id', 'appointments', ['agent_id'])
    op.create_index('idx_appointments_visitor_id', 'appointments', ['visitor_id'])
    op.create_index('idx_appointments_start', 'appointments', ['start_time'])
    op.create_index('idx_appointments_end', 'appointments', ['end_time'])

def downgrade():
    op.drop_index('idx_appointments_end', table_name='appointments')
    op.drop_index('idx_appointments_start', table_name='appointments')
    op.drop_index('idx_appointments_visitor_id', table_name='appointments')
    op.drop_index('idx_appointments_agent_id', table_name='appointments')
    op.drop_index('idx_appointments_smb_id', table_name='appointments')
    op.drop_constraint('check_calendar_json', 'appointments')
    op.drop_table('appointments')