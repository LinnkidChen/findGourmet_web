"""empty message

Revision ID: 607f066a4e16
Revises: bda1c921ce73
Create Date: 2022-12-05 20:46:57.297486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '607f066a4e16'
down_revision = 'bda1c921ce73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feeSummary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cityName', sa.Unicode(length=64), nullable=True),
    sa.Column('totalFee', sa.Integer(), nullable=True),
    sa.Column('Date', sa.DateTime(), nullable=True),
    sa.Column('type', sa.Unicode(length=32), nullable=True),
    sa.Column('modTime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('findG',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('type', sa.Unicode(length=32), nullable=True),
    sa.Column('name', sa.Unicode(length=64), nullable=True),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.Column('people', sa.Integer(), nullable=True),
    sa.Column('peopleCount', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('endTime', sa.DateTime(), nullable=True),
    sa.Column('createTime', sa.DateTime(), nullable=True),
    sa.Column('modifyTime', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Unicode(length=32), nullable=True),
    sa.Column('photos', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pleEat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('findG_id', sa.Integer(), nullable=True),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.Column('createTime', sa.DateTime(), nullable=True),
    sa.Column('modifyTime', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['findG_id'], ['findG.id'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('success',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('findGId', sa.Integer(), nullable=True),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('userId2', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('fee', sa.Integer(), nullable=True),
    sa.Column('fee2', sa.Integer(), nullable=True),
    sa.Column('cityName', sa.Unicode(length=64), nullable=True),
    sa.Column('type', sa.Unicode(length=32), nullable=True),
    sa.ForeignKeyConstraint(['findGId'], ['findG.id'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.ForeignKeyConstraint(['userId2'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('success_commenter',
    sa.Column('success_id', sa.Integer(), nullable=True),
    sa.Column('commentor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['commentor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['success_id'], ['success.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('success_commenter')
    op.drop_table('success')
    op.drop_table('pleEat')
    op.drop_table('findG')
    op.drop_table('feeSummary')
    # ### end Alembic commands ###
