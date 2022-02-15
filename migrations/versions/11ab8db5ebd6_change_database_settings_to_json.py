"""Change database settings to json

Revision ID: 11ab8db5ebd6
Revises: 46649f82d063
Create Date: 2022-02-15 14:52:00.067486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11ab8db5ebd6'
down_revision = '46649f82d063'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('database', sa.JSON(), nullable=True, default={'BACKUP_QUANTITY': 3}))

    op.execute("UPDATE system_settings SET database = '{\"BACKUP_QUANTITY\": 3}'")

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.alter_column('database', nullable=False)

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.drop_column('database_backup_quantity')


def downgrade():
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.drop_column('database')

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('database_backup_quantity', sa.Integer(), nullable=True, default=3))

    op.execute("UPDATE system_settings SET database_backup_quantity = 3")

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.alter_column('database_backup_quantity', nullable=False)
