"""empty message

Revision ID: 1e480ccc916b
Revises: 51b4aa38d644
Create Date: 2022-01-24 10:43:50.431545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e480ccc916b'
down_revision = '51b4aa38d644'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('item', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_item_name'), ['name'])

    with op.batch_alter_table('item_category', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_item_category_name'), ['name'])

    with op.batch_alter_table('item_location', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_item_location_name'), ['name'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('setting_id', sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_user_email'), ['email'])
        batch_op.create_unique_constraint(batch_op.f('uq_user_username'), ['username'])
        batch_op.create_foreign_key(batch_op.f('fk_user_setting_id_user_settings'), 'user_settings', ['setting_id'], ['id'])

    with op.batch_alter_table('user_group', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_user_group_name'), ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_group', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_user_group_name'), type_='unique')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_user_setting_id_user_settings'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('uq_user_username'), type_='unique')
        batch_op.drop_constraint(batch_op.f('uq_user_email'), type_='unique')
        batch_op.drop_column('setting_id')

    with op.batch_alter_table('item_location', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_item_location_name'), type_='unique')

    with op.batch_alter_table('item_category', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_item_category_name'), type_='unique')

    with op.batch_alter_table('item', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_item_name'), type_='unique')

    # ### end Alembic commands ###