"""First migration

Revision ID: 07abf5513c91
Revises: 
Create Date: 2024-10-18 13:32:03.195358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07abf5513c91'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('operations',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('operator_id', sa.String(), nullable=True),
    sa.Column('required_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('annual_interest', sa.DECIMAL(precision=5, scale=2), nullable=False),
    sa.Column('deadline', sa.Date(), nullable=False),
    sa.Column('current_amount', sa.DECIMAL(precision=15, scale=2), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bids',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('investor_id', sa.String(), nullable=True),
    sa.Column('operation_id', sa.String(), nullable=True),
    sa.Column('invested_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('interest_rate', sa.DECIMAL(precision=5, scale=2), nullable=False),
    sa.Column('bid_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['investor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['operation_id'], ['operations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bids')
    op.drop_table('operations')
    op.drop_table('users')
    # ### end Alembic commands ###
