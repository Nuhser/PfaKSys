"""empty message

Revision ID: 57c1086a0a6b
Revises: 
Create Date: 2022-01-24 10:30:59.163658

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '57c1086a0a6b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_settings')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_settings',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('language', sa.VARCHAR(length=2), nullable=True),
    sa.Column('item_filters', sqlite.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['item_location.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
