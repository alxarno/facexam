from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
users_info_page = Table('users_info_page', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('photo', String(length=64), nullable=False),
    Column('about', String(length=256), nullable=False),
    Column('user_active_achivs', String(length=256)),
    Column('user_active_background', String(length=20)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['users_info_page'].columns['user_active_background'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['users_info_page'].columns['user_active_background'].drop()
