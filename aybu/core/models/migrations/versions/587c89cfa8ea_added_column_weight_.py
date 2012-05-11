"""Added column 'weight' to Banner, Logo and Background.

Revision ID: 587c89cfa8ea
Revises: 2c0bfc379e01
Create Date: 2012-05-11 14:36:15.518757

"""

# downgrade revision identifier, used by Alembic.
revision = '587c89cfa8ea'
down_revision = '2c0bfc379e01'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('weight', sa.Integer(),
                                     nullable=False, default=0))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'weight')
    ### end Alembic commands ###