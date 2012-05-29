"""No unique on SimpleMixin.weight

Revision ID: 1e57df57979b
Revises: 587c89cfa8ea
Create Date: 2012-05-29 13:27:36.878552

"""

# downgrade revision identifier, used by Alembic.
revision = '1e57df57979b'
down_revision = '587c89cfa8ea'

from alembic import op


def upgrade():
    connection = op.get_bind()
    result = connection.execute(
        "SELECT relname \
         FROM pg_class \
         WHERE oid IN (SELECT indexrelid \
                       FROM pg_index, pg_class \
                       WHERE pg_class.relname='files' AND \
                             pg_class.oid=pg_index.indrelid AND \
                             indisunique = 't') \
               AND relname='files_weight_key';"
    )
    if result.fetchone():
        op.drop_constraint('files_weight_key', 'files')


def downgrade():
    pass
