"""Changed settings table to handle bigger data

Revision ID: 2637e08f3c15
Revises: 26486ceb6dac
Create Date: 2012-02-15 09:50:38.527625

"""

# downgrade revision identifier, used by Alembic.
revision = '2637e08f3c15'
down_revision = '26486ceb6dac'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('settings', 'value', type_=sa.Unicode(1024),
                    existing_server_default=None, existing_nullable=False)


def downgrade():
    op.alter_column('settings', 'value', type_=sa.Unicode(512),
                    existing_server_default=None, existing_nullable=False)
