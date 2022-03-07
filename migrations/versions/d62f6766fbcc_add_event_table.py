"""Add event table

Revision ID: d62f6766fbcc
Revises: d39ee32c75d5
Create Date: 2022-02-22 18:12:46.707128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd62f6766fbcc'
down_revision = 'd39ee32c75d5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('date_start', sa.DateTime(), nullable=False),
        sa.Column('date_end', sa.DateTime()),
        sa.Column('location', sa.String()),
        sa.Column('sync_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_event'))
    )


def downgrade():
    op.drop_table('event')
