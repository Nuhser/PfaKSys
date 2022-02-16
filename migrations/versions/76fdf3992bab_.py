"""empty message

Revision ID: 76fdf3992bab
Revises: 1e480ccc916b
Create Date: 2022-01-27 12:05:33.967430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76fdf3992bab'
down_revision = '1e480ccc916b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    system_settings = op.create_table('system_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mail', sa.JSON(), nullable=False),
    sa.Column('calendar', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_system_settings'))
    )
    # ### end Alembic commands ###
    
    op.execute(
        system_settings.insert().values(
            mail={'MAIL_SERVER': None, 'MAIL_PORT': 587, 'MAIL_USE_TLS': True, 'MAIL_USE_SSL': True, 'MAIL_SENDER': None},
            calendar={'CALENDAR_LINK': None, 'CALENDAR_CATEGORIES': [], 'CALENDAR_SYNC_INTERVALL': 5}
        )
    )



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('system_settings')
    # ### end Alembic commands ###
