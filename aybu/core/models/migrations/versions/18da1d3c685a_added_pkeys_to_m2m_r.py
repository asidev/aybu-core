"""Added pkeys to m2m rel

Revision ID: 18da1d3c685a
Revises: 2637e08f3c15
Create Date: 2012-03-15 22:47:08.646132

"""

# downgrade revision identifier, used by Alembic.
revision = '18da1d3c685a'
down_revision = '2637e08f3c15'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table(u'node_infos__keywords')
    op.drop_table(u'keywords')
    op.alter_column('node_infos_files__files', u'files_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('node_infos_files__files', u'node_infos_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('node_infos_images__files', u'files_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('node_infos_images__files', u'node_infos_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('node_infos_links__node_infos', u'links_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('node_infos_links__node_infos', u'inverse_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('nodes_banners__files', u'nodes_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('nodes_banners__files', u'files_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    connection = op.get_bind()
    for table, fields in {
        'node_infos_files__files': ('files_id', 'node_infos_id'),
        'node_infos_images__files': ('files_id', 'node_infos_id'),
        'node_infos_links__node_infos': ('links_id', 'inverse_id'),
        'nodes_banners__files': ('nodes_id', 'files_id')}.items():

        connection.execute('ALTER TABLE {0} ADD CONSTRAINT {0}_pkey '
                           'PRIMARY KEY ({1}, {2});'.format(table, fields[0],
                                                           fields[1]))


def downgrade():
    op.create_table(u'keywords',
    sa.Column(u'name', sa.VARCHAR(length=64), nullable=False),
    sa.PrimaryKeyConstraint(u'name', name=u'keywords_pkey')
    )
    op.create_table(u'node_infos__keywords',
    sa.Column(u'node_infos_id', sa.INTEGER(), nullable=True),
    sa.Column(u'keyword_name', sa.VARCHAR(length=64), nullable=True),
    sa.ForeignKeyConstraint(['keyword_name'], [u'keywords.name'],
                            name=u'node_infos__keywords_keyword_name_fkey'),
    sa.ForeignKeyConstraint(['node_infos_id'], [u'node_infos.id'],
                            name=u'node_infos__keywords_node_infos_id_fkey'),
    sa.PrimaryKeyConstraint()
    )
    op.alter_column('node_infos_files__files', u'files_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('node_infos_files__files', u'node_infos_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('node_infos_images__files', u'files_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('node_infos_images__files', u'node_infos_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('node_infos_links__node_infos', u'links_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('node_infos_links__node_infos', u'inverse_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('nodes_banners__files', u'nodes_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('nodes_banners__files', u'files_id',
               existing_type=sa.INTEGER(),
               nullable=True)
