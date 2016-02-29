from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import metadata
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.types import DateTime
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode

# WARNING COMPLETELY UNTESTED!!
songs = Table('songs', metadata,
    Column(
        'id',
        BIGINT(unsigned=True),
        autoincrement=True,
        primary_key=True,
    ),
    Column(
        'filename',
        Unicode(256),
        nullable=False,
    ),
    Column(
        'title',
        Unicode(256),
        nullable=False,
    ),
    Column(
        'artist_id',
        BIGINT(unsigned=True),
        ForeignKey(
            'artists.id',
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False
    ),
    Column(
        'duration',
        Integer,
        default=0,
        nullable=False,
    ),
    Column(
        'date_added',
        DateTime,
    ),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
