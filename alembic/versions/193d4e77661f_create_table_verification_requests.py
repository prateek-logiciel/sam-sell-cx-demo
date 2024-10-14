"""create table verification_requests

Revision ID: 193d4e77661f
Revises: a22d01818916
Create Date: 2024-09-02 16:39:11.592047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '193d4e77661f'
down_revision: Union[str, None] = 'a22d01818916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'verification_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('visitor_id', sa.Integer(), sa.ForeignKey('visitors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(5), nullable=False),
        sa.Column('contact', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('expired_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('status', sa.String(10), server_default='open', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ['visitor_id'], 
            ['visitors.id'], 
            ondelete='CASCADE'
        ),
        sa.CheckConstraint(
            "status IN ('open', 'completed')", 
            name='verification_requests_status_check'
        ),
        sa.CheckConstraint(
            "type IN ('email', 'phone')", 
            name='verification_requests_type_check'
        )
    )

def downgrade() -> None:
    op.drop_table('verification_requests')