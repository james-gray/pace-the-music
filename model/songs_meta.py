from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import metadata
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.types import Integer

# WARNING COMPLETELY UNTESTED!!
songs_meta = Table('songs_meta', metadata,
    Column(
        'id',
        BIGINT(unsigned=True),
        autoincrement=True,
        primary_key=True,
    ),
    Column(
        'song_id',
        BIGINT(unsigned=True),
        ForeignKey(
            'songs.id',
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False,
    ),
    Column(
        'bpm',
        Integer,
        default=0,
    ),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
