from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
document = Table('document', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=128)),
    Column('type', VARCHAR(length=5)),
    Column('size', INTEGER),
    Column('downloads', INTEGER),
    Column('path', VARCHAR(length=256)),
    Column('upload_on', DATETIME),
)

document = Table('document', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=128)),
    Column('doctype', String(length=5)),
    Column('size', Integer),
    Column('downloads', Integer),
    Column('path', String(length=256)),
    Column('upload_on', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['document'].columns['type'].drop()
    post_meta.tables['document'].columns['doctype'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['document'].columns['type'].create()
    post_meta.tables['document'].columns['doctype'].drop()
