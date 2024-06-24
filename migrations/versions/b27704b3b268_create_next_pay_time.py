"""create next_pay_time

Revision ID: b27704b3b268
Revises: 60923c9e2da0
Create Date: 2022-11-13 22:15:45.834083

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b27704b3b268'
down_revision = '60923c9e2da0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organizations', sa.Column('next_pay_time', sa.DateTime(), nullable=True))
    op.drop_column('organizations', 'last_pay_time')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organizations', sa.Column('last_pay_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('organizations', 'next_pay_time')
    # ### end Alembic commands ###
