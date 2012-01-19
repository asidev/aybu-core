"""empty message

Revision ID: 26486ceb6dac
Revises: None
Create Date: 2011-12-08 16:02:11.425157

"""

# downgrade revision identifier, used by Alembic.
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('languages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.Unicode(length=2), nullable=False),
        sa.Column('country', sa.Unicode(length=2), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.UniqueConstraint('lang', 'country'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('views',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=True),
        sa.Column('fs_view_path', sa.String(length=255), nullable=True),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('fs_view_path'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('views_descriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.UnicodeText(), nullable=True),
        sa.Column('view_id', sa.Integer(), nullable=True),
        sa.Column('lang_id', sa.Integer(), nullable=True),
        sa.UniqueConstraint('view_id', 'lang_id'),
        sa.ForeignKeyConstraint(['lang_id'], ['languages.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['view_id'], ['views.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('setting_types',
        sa.Column('name', sa.Unicode(length=64), nullable=False),
        sa.Column('raw_type', sa.String(length=8), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )

    op.create_table('settings',
        sa.Column('name', sa.Unicode(length=128), nullable=False),
        sa.Column('value', sa.Unicode(length=512), nullable=False),
        sa.Column('ui_administrable', sa.Boolean(), nullable=True),
        sa.Column('type_name', sa.Unicode(length=64), nullable=True),
        sa.ForeignKeyConstraint(['type_name'], ['setting_types.name'],
                                onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('name')
    )

    op.create_table('keywords',
        sa.Column('name', sa.Unicode(length=64), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )

    op.create_table('groups',
        sa.Column('name', sa.Unicode(length=32), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )

    op.create_table('users',
        sa.Column('username', sa.Unicode(length=255), nullable=False),
        sa.Column('password', sa.Unicode(length=128), nullable=False),
        sa.PrimaryKeyConstraint('username')
    )

    op.create_table('users_groups',
        sa.Column('users_username', sa.Unicode(length=255), nullable=True),
        sa.Column('groups_name', sa.Unicode(length=32), nullable=True),
        sa.ForeignKeyConstraint(['groups_name'], ['groups.name'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['users_username'], ['users.username'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('users_username', 'groups_name')
    )

    themes_primary = sa.Column('name', sa.Unicode(length=128), nullable=False)
    op.create_table('themes',
        themes_primary,
        sa.Column('parent_name', sa.Unicode(length=128), nullable=True),
        sa.ForeignKeyConstraint(['parent_name'], [themes_primary], ),
        sa.PrimaryKeyConstraint('name')
    )

    op.create_table('files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.Unicode(length=128), nullable=True),
        sa.Column('name', sa.Unicode(length=128), nullable=False),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('row_type', sa.Unicode(length=50), nullable=True),
        sa.Column('default', sa.Boolean(), nullable=True),
#        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id')
    )

    nodes_primary = sa.Column('id', sa.Integer(), nullable=False)
    op.create_table('nodes',
        sa.Column('row_type', sa.String(length=50), nullable=True),
        nodes_primary,
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('hidden', sa.Boolean(), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('home', sa.Boolean(), nullable=True),
        sa.Column('sitemap_priority', sa.Integer(), nullable=True),
        sa.Column('view_id', sa.Integer(), nullable=True),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.Column('collection_id', sa.Integer(), nullable=True),
        sa.Column('linked_to_id', sa.Integer(), nullable=True),
#        sa.CheckConstraint('TODO'),
#        sa.CheckConstraint('TODO'),
#        sa.CheckConstraint('TODO'),
        sa.UniqueConstraint('parent_id', 'weight'),
        sa.ForeignKeyConstraint(['collection_id'], [nodes_primary],
                                onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['linked_to_id'], [nodes_primary],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], [nodes_primary], ),
        sa.ForeignKeyConstraint(['view_id'], ['views.id'], onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('node_infos',
        sa.Column('row_type', sa.String(length=50), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.Unicode(length=64), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('lang_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=64), nullable=True),
        sa.Column('url_part', sa.Unicode(length=64), nullable=True),
        sa.Column('parent_url', sa.Unicode(length=512), nullable=True),
        sa.Column('meta_description', sa.UnicodeText(), nullable=True),
        sa.Column('head_content', sa.UnicodeText(), nullable=True),
        sa.Column('content', sa.UnicodeText(), nullable=True),
        sa.Column('ext_url', sa.Unicode(length=512), nullable=True),
        sa.ForeignKeyConstraint(['lang_id'], ['languages.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.id'], onupdate='CASCADE',
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('node_infos_links__node_infos',
        sa.Column('inverse_id', sa.Integer(), nullable=True),
        sa.Column('links_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['inverse_id'], ['node_infos.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['links_id'], ['node_infos.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint()
    )

    op.create_table('node_infos_images__files',
        sa.Column('node_infos_id', sa.Integer(), nullable=True),
        sa.Column('files_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['files_id'], ['files.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_infos_id'], ['node_infos.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint()
    )

    op.create_table('node_infos_files__files',
        sa.Column('node_infos_id', sa.Integer(), nullable=True),
        sa.Column('files_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['files_id'], ['files.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_infos_id'], ['node_infos.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint()
    )

    op.create_table('node_infos__keywords',
        sa.Column('node_infos_id', sa.Integer(), nullable=True),
        sa.Column('keyword_name', sa.Unicode(length=64), nullable=True),
        sa.ForeignKeyConstraint(['keyword_name'], ['keywords.name'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_infos_id'], ['node_infos.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint()
    )

    op.create_table('nodes_banners__files',
        sa.Column('nodes_id', sa.Integer(), nullable=True),
        sa.Column('files_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['files_id'], ['files.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['nodes_id'], ['nodes.id'],
                                onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint()
    )

def downgrade():
    op.drop_table('node_infos_links__node_infos')
    op.drop_table('node_infos_images__files')
    op.drop_table('node_infos_files__files')
    op.drop_table('node_infos__keywords')
    op.drop_table('nodes_banners__files')
    op.drop_table('settings')
    op.drop_table('setting_types')
    op.drop_table('users_groups')
    op.drop_table('users')
    op.drop_table('groups')
    op.drop_table('themes')
    op.drop_table('keywords')
    op.drop_table('node_infos')
    op.drop_table('nodes')
    op.drop_table('files')
    op.drop_table('views_descriptions')
    op.drop_table('views')
    op.drop_table('languages')
