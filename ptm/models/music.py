from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from ptm.models.base import Base
from ptm.models.base import PtmBase
from ptm.models.base import session

class Artist(Base, PtmBase):
    """
    An Artist object representing a music artist. A single instance can be the
    Artist for many Songs.
    """
    __tablename__ = 'artists'

    # State
    name = Column(String, nullable=False)

    # Relationships
    songs = relationship('Song', back_populates='artist')

    # Behaviour
    def __repr__(self):
        return '<Artist(name="%s")>' % self.name

class Playlist(Base, PtmBase):
    """
    A Playlist object representing a playlist of Songs.
    """
    __tablename__ = 'playlists'

    # State
    name = Column(String, nullable=False) # User-specified playlist name

    # Relationships
    playlist_songs = relationship('PlaylistSong', order_by='PlaylistSong.position',
                         collection_class=ordering_list('position'))

    @property
    def songs(self):
        return [ps.song for ps in self.playlist_songs]

    # Behaviour
    def __repr__(self):
        return '<Playlist(name="%s")>' % self.name

    def append_song(self, song):
        """
        Append song `song` to the playlist.
        """
        ps = PlaylistSong(playlist=self, song=song)
        self.playlist_songs.append(ps)
        session.flush()

    def insert_song(self, position, song):
        """
        Insert song `song` at position `position`
        """
        ps = PlaylistSong(playlist=self, song=song)
        self.playlist_songs.insert(position, ps)
        session.flush()

    def delete_song(self, position):
        """
        Delete the song at position `position`.
        """
        ps = self.playlist_songs.pop(position)
        session.delete(ps)
        session.flush()

class PlaylistSong(Base, PtmBase):
    """
    A many-to-many join table that maps Playlists to their Songs.
    """
    __tablename__ = 'playlists_songs'

    # State
    playlist_id = Column(Integer, ForeignKey('playlists.id'), nullable=False)
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    position = Column(Integer)

    # Relationships
    playlist = relationship('Playlist')
    song = relationship('Song')

    # Behaviour
    def __repr__(self):
        return '<PlaylistSong(song="%s")>' % self.song.title

    @classmethod
    def remove_orphans(cls):
        """
        Remove 'orphaned' PlaylistSongs (i.e. entries with no playlist_id.)

        It isn't really a big deal if we have orphans in the database, however
        they can be removed using this method if needed.
        """
        cls.query.filter(cls.playlist_id == None).delete(synchronize_session='fetch')

class Song(Base, PtmBase):
    """
    A Song object representing a song in the library. Each song has a parent
    Artist as well as a SongMeta.
    """
    __tablename__ = 'songs'

    # State
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

class SongMeta(Base, PtmBase):
    """
    Metadata for a Song. There exists a one-to-one mapping of Songs to their
    SongMetas.
    """
    __tablename__ = 'songs_meta'

    # State
    duration = Column(Integer) # Duration in seconds
    bpm = Column(Float) # The BPM of the song
    energy = Column(Float) # Energy of the song (float value between 0 and 1)
    song_id = Column(Integer, ForeignKey('songs.id'))

    # Relationships
    song = relationship('Song', back_populates='meta')
