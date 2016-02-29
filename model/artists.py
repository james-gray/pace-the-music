from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import metadata
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.types import Unicode

# WARNING COMPLETELY UNTESTED!!
artists = Table('artists', metadata,
    Column(
        'id',
        BIGINT(unsigned=True),
        autoincrement=True,
        primary_key=True,
    ),
    Column(
        'name',
        Unicode(256),
        nullable=False,
    ),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
