import os
import random

from collections import OrderedDict

from ConfigParser import ConfigParser

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from ptm.models.base import Base
from ptm.models.base import PtmBase
from ptm.models.base import session

config = ConfigParser()

# Enumeration for comparing paces with respect to speed (i.e. Slow is
# 'less than' Steady)
PACE_ENUM = OrderedDict([
    ('Slow', 0),
    ('Steady', 1),
    ('Fast', 2),
    ('Sprint', 3),
])

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

    __table_args__ = (
        UniqueConstraint('name', name='artist_name'),
    )

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

    def generate(self, plan):
        """
        Generate a playlist of songs given a plan.
        """
        def get_current_set(sets, pace):
            """
            Return the set of songs for the given Pace if non-empty, otherwise
            choose sets in increasing order of speed until a non-empty set is
            found. If all sets are empty, return `None`.

            Nested because it only makes sense to use this within generate().
            """
            if sets[pace]:
                # Current set is non-empty - guard statement returns early
                return sets[pace]

            # The set for the current segment pace is empty - choose the
            # next fastest set
            print "    NO SONGS LEFT IN CURRENT SET %s! Choosing a new set" % pace
            paces = PACE_ENUM.keys()
            for _ in xrange(4):
                # Get new pace using the PACE_ENUM.
                # Choose the next paces in increasing speed order, unless the
                # current pace is a Sprint, in which case we wrap around to Slow.
                pace = paces[(paces.index(pace) + 1) % 4] # modulo to wrap around to Slow
                if sets[pace]:
                    # We have found a non-empty set - continue with this
                    print "        Found nonempty set %s" % pace
                    return sets[pace]
            else:
                # At this point NONE of the pace sets had any songs left,
                # which means we have exhausted our corpus of songs.
                # Break here - the playlist is finished as there's nothing
                # left to add.
                print "        ALL SETS EXHAUSTED"
                return None


        # Reset the playlist, just in case!
        for _ in xrange(len(self.playlist_songs)):
            ps = self.playlist_songs.pop()
            session.delete(ps)
        self.playlist_songs = []
        session.flush()

        slow_set, steady_set, fast_set, sprint_set = self.divide_songs_into_sets()
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

            current_set = get_current_set(sets, pace)
            if not current_set:
                # We have exhausted the corpus of songs! Our playlist is finished
                break

            # Pick subset of songs that can fit in the time remaining
            subset = [
                song
                for song in current_set
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
                current_set.remove(song)

                # Recalculate time remaining
                remaining_time -= song.meta.duration

                # Remove any songs that are greater than the remaining time
                subset = [
                    song
                    for song in subset
                    if song.meta.duration <= remaining_time
                ]

            # At this point the segment cannot fit any more segments without
            # overlapping with the next segment.
            print "    Cannot fit any more whole songs in this segment."

            # It's possible at this point that the current set has been exhausted
            # of songs, so we check to see if we need to get the next nonempty set
            current_set = get_current_set(sets, pace)
            if not current_set:
                # No more songs
                break

            if remaining_time == 0 and remaining_segments > 0:
                # Just go to the next seg - set remaining_time to that segment's
                # duration
                remaining_time = segments[seg.position + 1].length
                print "        Moving to next segment"
            elif remaining_segments == 0:
                # Our run is almost done - pick a random song at the current
                # segment pace
                song = random.choice(current_set)
                self.append_song(song)
                current_set.remove(song)
                print "        THIS IS THE LAST SEGMENT. Adding random song"
            else:
                # We will (potentially) have to overlap with the next segment.
                next_seg = segments[seg.position + 1]
                if PACE_ENUM[next_seg.pace.speed] > PACE_ENUM[seg.pace.speed] \
                        and current_set[0].meta.duration / 2 > remaining_time:
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
                    song = current_set[0]
                    self.append_song(song)
                    current_set.remove(song)
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

        self.write_playlist_to_file()

    def write_playlist_to_file(self):
        """
        Write the generated playlist to a .pls file.
        A .pls file is essentially an .ini file, so we write it using ConfigParser.
        See https://en.wikipedia.org/wiki/PLS_%28file_format%29.
        """
        section = u'playlist'
        if not config.has_section(section):
            config.add_section(section) # Add required [playlist] header

        for i, song in enumerate(self.songs):
            # Add the required File, Title, and Length sections for each song, as per
            # the PLS spec
            config.set(section, 'File%s' % str(i+1), os.path.join('file:///', song.filename.encode('utf-8')[1:]))
            config.set(section, 'Title%s' % str(i+1), song.title.encode('utf-8'))
            config.set(section, 'Length%s' % str(i+1), song.meta.duration)

        # Add required additional sections
        config.set(section, 'NumberOfEntries', len(self.songs))
        config.set(section, 'Version', 2)

        # Write the config file to a temporary file
        tmpfile = 'playlists/%s-tmp.pls' % self.name
        with open(tmpfile, 'w') as tmp:
            config.write(tmp)

        with open('playlists/%s.pls' % self.name, 'w') as pls:
            # Silly hack to get around the fact that you can't actually
            # write INI files without spaces after the = signs using ConfigParser
            tmp = open(tmpfile, 'r')
            for line in tmp:
                pls.write(line.replace(' = ', '=', 1))
            tmp.close()
            os.remove(tmpfile)

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
