"""create table address

Revision ID: c345712aff7f
Revises: a4f9a88e860e
Create Date: 2024-09-16 19:29:04.654076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c345712aff7f'
down_revision: Union[str, None] = 'a4f9a88e860e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Create the 'address' table
    op.create_table(
        'address',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('zipcode', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop the 'address' table
    op.drop_table('address')