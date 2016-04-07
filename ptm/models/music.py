import random

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

    def generate(self, plan):
        """
        Generate a playlist of songs given a plan.
        """
        slow_set, steady_set, fast_set, sprint_set = self.divide_songs_into_sets()
        # Enumeration for comparing paces with respect to speed (i.e. Slow is
        # 'less than' Steady)
        pace_enum = {
            'Slow': 1,
            'Steady': 2,
            'Fast': 3,
            'Sprint': 4,
        }
        # Add sets to a dict to easily access by hash
        sets = {
            'Slow': slow_set,
            'Steady': steady_set,
            'Fast': fast_set,
            'Sprint': sprint_set,
        }
        segments = list(plan.segments)
        remaining_segments = len(segments)

        remaining_time = segments[0].length
        skips = 0
        for seg in segments:
            if skips > 0:
                # Skip this segment if a song overlaps it completely
                skips -= 1
                continue

            print "NEW SEGMENT: %s" % seg
            remaining_segments -= 1
            pace = seg.pace.speed
            # Pick subset of songs that can fit in the time remaining
            subset = [
                song
                for song in sets[pace]
                if song.meta.duration <= remaining_time
            ]

            while subset:
                # Pick a random song
                song = random.choice(subset)

                # Add the song to our playlist
                print "    Adding song from subset: %s" % song
                self.append_song(song)

                # Remove the song from relevant sets
                subset.remove(song)
                sets[pace].remove(song)

                # Recalculate time remaining
                remaining_time -= song.meta.duration

                # Remove any songs that are greater than the remaining time
                subset = [
                    song
                    for song in subset
                    if song.meta.duration <= remaining_time
                ]

            print "    Cannot fit any more whole songs in this segment."

            # At this point the segment cannot fit any more segments without
            # overlapping with the next segment.
            if remaining_time == 0:
                # Just go to the next seg - set remaining_time to that segment's
                # duration
                remaining_time = segments[seg.position + 1].length
                print "        Moving to next segment"
            elif remaining_segments == 0:
                # Our run is almost done - pick a random song at the current
                # segment pace
                song = random.choice(sets[pace])
                self.append_song(song)
                sets[pace].remove(song)
                print "        THIS IS THE LAST SEGMENT. Adding random song"
            else:
                next_seg = segments[seg.position + 1]
                if pace_enum[next_seg.pace.speed] > pace_enum[seg.pace.speed] \
                        and sets[pace][0].meta.duration / 2 > remaining_time:
                    # The next segment is at a faster pace.
                    # Here we choose a song from the current segment's set iff
                    # 50% or more of the song will take place in the current
                    # segment.
                    next_pace = next_seg.pace.speed
                    song = sets[next_pace][0]
                    self.append_song(song)
                    sets[next_pace].remove(song)
                    print "        Next segment is faster, add song from next pace."
                else:
                    # Pick the shortest song from the current pace's set, so we
                    # minimize the amount of time the song cuts into the next
                    # segment
                    song = sets[pace][0]
                    self.append_song(song)
                    sets[pace].remove(song)
                    print "        Add song from curr pace."

                # Calculate the overlap between the last song of this segment
                # and the next segment
                overlap = (song.meta.duration - remaining_time)
                next_seg_position = seg.position + 1
                remaining_time = segments[next_seg_position].length - overlap
                while remaining_time <= 0:
                    # If the song completely overlaps the next segment, skip it
                    # and consider the segment after that, until we no longer
                    # completely overlap any segments.
                    print "SKIPPING %s" % segments[next_seg_position]
                    skips += 1
                    remaining_segments -= 1
                    if remaining_segments == 0:
                        # We have already overlapped the last segment, so no more
                        # songs are needed
                        return
                    next_seg_position += 1
                    overlap = abs(remaining_time)
                    remaining_time = segments[next_seg_position].length - overlap

    def divide_songs_into_sets(self):
        """
        Divide the Songs in the database into four sets such that the
        bottom 30% of songs will be considered for 'slow' paces, the
        next 30% for 'steady', the next 30% for 'fast' and the final
        10% for 'sprint'. The sets are based on the relative
        distribution of BPM values of songs.
        """
        songs = sorted(Song.query.all(), key=lambda song: song.meta.bpm)

        lim = int((len(songs)*3)/10)
        # Slow
        slow_songs = songs[:lim]
        # Steady
        steady_songs = songs[lim+1:lim*2]
        # Fast
        fast_songs = songs[(lim*2)+1:lim*3]
        # Sprint
        sprint_songs = songs[(lim*3)+1:]

        # Sort the subsets by song length
        return [
            sorted(subset, key=lambda song: song.meta.duration)
            for subset in (slow_songs, steady_songs, fast_songs, sprint_songs)
        ]

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

        Ideally this won't need to be used if you only add/remove playlists_songs
        using methods of Playlist, however if for whatever reason you end up with
        orphans you can use this method.
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
    song_id = Column(Integer, ForeignKey('songs.id'))

    # Relationships
    song = relationship('Song', back_populates='meta')
