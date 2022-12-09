"""empty message

Revision ID: 181488197283
Revises: 607f066a4e16
Create Date: 2022-12-08 13:00:08.008291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '181488197283'
down_revision = '607f066a4e16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feeSummary', sa.Column('count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feeSummary', 'count')
    # ### end Alembic commands ###