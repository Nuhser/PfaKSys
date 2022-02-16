"""Add notification settings to system settings

Revision ID: d39ee32c75d5
Revises: 11ab8db5ebd6
Create Date: 2022-02-16 14:49:07.413399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd39ee32c75d5'
down_revision = '11ab8db5ebd6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notifications', sa.JSON(), nullable=True, default={'NEW_USER': True}))

    op.execute("UPDATE system_settings SET notifications = '{\"NEW_USER\": true}'")

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.alter_column('notifications', nullable=False)


def downgrade():
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.drop_column('notifications')
