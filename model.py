from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode

Base = declarative_base()

class Artist(Base):
    """
    An Artist object representing a music artist. A single instance can be the
    Artist for many Songs.
    """
    __tablename__ = 'artists'

    # State
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(Unicode(250), nullable=False)

    # Behaviour
    def __repr__(self):
        return '<Artist(name="%s")' % self.name

class Song(Base):
    """
    A Song object representing a song in the library. Each song has a parent
    Artist as well as a SongMeta.
    """
    __tablename__ = 'songs'

    # State
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    filename = Column(Unicode(250), nullable=False)
    title = Column(Unicode(250))
    duration = Column(Integer, default=0, nullable=False)
    date_added = Column(DateTime, nullable=False)
    artist_id = Column(BIGINT, ForeignKey('artist.id'))

    # Relationships
    artist = relationship('Artist', back_populates='songs')
    # One-to-one relationship of a song to its metadata.
    # See http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-one
    meta = relationship('SongMeta', uselist=False, back_populates='song')

    # Behaviour
    def __repr__(self):
        return '<Song(filename="%s")>' % self.filename

class SongMeta(Base):
    """
    Metadata for a Song. There exists a one-to-one mapping of Songs to their
    SongMetas.
    """
    __tablename__ = 'songs_meta'

    # State
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    bpm = Column(Integer, default=0)
    song_id = Column(BIGINT, ForeignKey('song.id'))

    # Relationships
    song = relationship('Song', back_populates='meta')

Artist.songs = relationship('Song', order_by=Song.id, back_populates='artist')
