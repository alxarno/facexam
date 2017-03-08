from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
subjects = Table('subjects', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64), nullable=False),
)

subjects_themes = Table('subjects_themes', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64), nullable=False),
    Column('subject_id', Integer),
)

themes_lections = Table('themes_lections', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64), nullable=False),
    Column('content', String(length=10000)),
    Column('themes_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['subjects'].create()
    post_meta.tables['subjects_themes'].create()
    post_meta.tables['themes_lections'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['subjects'].drop()
    post_meta.tables['subjects_themes'].drop()
    post_meta.tables['themes_lections'].drop()
