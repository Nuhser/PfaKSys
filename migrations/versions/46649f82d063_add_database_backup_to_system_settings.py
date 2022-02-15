"""Add database backup to system settings

Revision ID: 46649f82d063
Revises: 
Create Date: 2022-02-04 15:16:25.877840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46649f82d063'
down_revision = '3da908a0ed34'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('database_backup_quantity', sa.Integer(), nullable=True, default=3))

    op.execute("UPDATE system_settings SET database_backup_quantity = 3")

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.alter_column('database_backup_quantity', nullable=False)



def downgrade():
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.drop_column('database_backup_quantity')
