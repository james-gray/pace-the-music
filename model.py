from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import String

Base = declarative_base()

class Artist(Base):
    """
    An Artist object representing a music artist. A single instance can be the
    Artist for many Songs.
    """
    __tablename__ = 'artists'

    # State
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Behaviour
    def __repr__(self):
        return '<Artist(name="%s")>' % self.name

class Song(Base):
    """
    A Song object representing a song in the library. Each song has a parent
    Artist as well as a SongMeta.
    """
    __tablename__ = 'songs'

    # State
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    title = Column(String)
    date_added = Column(DateTime, nullable=False)
    artist_id = Column(Integer, ForeignKey('artists.id'))

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
    id = Column(Integer, primary_key=True)
    duration = Column(Integer)
    bpm = Column(Float) # The BPM of the song
    energy = Column(Float) # Energy of the song (float value between 0 and 1)
    song_id = Column(Integer, ForeignKey('songs.id'))

    # Relationships
    song = relationship('Song', back_populates='meta')

Artist.songs = relationship('Song', order_by=Song.id, back_populates='artist')
