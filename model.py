from sqlalchemy import sql
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from config import db

engine = create_engine('sqlite:///%s' % db['path'], echo=True)
DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()

Base = declarative_base()

class Artist(Base):
    """
    An Artist object representing a music artist. A single instance can be the
    Artist for many Songs.
    """
    __tablename__ = 'artists'
    query = DBSession.query_property()

    # State
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Relationships
    songs = relationship('Song', back_populates='artist')

    # Behaviour
    def __repr__(self):
        return '<Artist(name="%s")>' % self.name

class Song(Base):
    """
    A Song object representing a song in the library. Each song has a parent
    Artist as well as a SongMeta.
    """
    __tablename__ = 'songs'
    query = DBSession.query_property()

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
    query = DBSession.query_property()

    # State
    id = Column(Integer, primary_key=True)
    duration = Column(Integer) # Duration in seconds
    bpm = Column(Float) # The BPM of the song
    energy = Column(Float) # Energy of the song (float value between 0 and 1)
    song_id = Column(Integer, ForeignKey('songs.id'))

    # Relationships
    song = relationship('Song', back_populates='meta')

class Pace(Base):
    """
    Pace object to be used in a Segment. One of: Slow, Steady, Fast, Sprint.
    """
    __tablename__ = 'paces'
    query = DBSession.query_property()

    # State
    id = Column(Integer, primary_key=True)
    speed = Column(String, nullable=False)

class ActivityPlan(Base):
    """
    Named activity plan object which will be associated with several Segments
    via the plans_segments join table.
    """
    __tablename__ = 'activity_plans'
    query = DBSession.query_property()

    # State
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False) # User-specified plan name (e.g. "HIIT Run")
    num_segments = Column(Integer, default=0, nullable=False)

    def add_segment(self, pace, length):
        prev = None if self.num_segments == 0 else self.last_segment
        seg = Segment(
            plan=self,
            pace=pace,
            length=length,
            prev=prev,
            next=None,
        )

        if prev:
            prev.next = seg
            session.add(prev)

        self.num_segments += 1
        session.add(self)
        session.add(seg)
        session.commit()

    @hybrid_property
    def segments(self):
        segments = []
        if self.num_segments == 0:
            return segments

        seg = Segment.query.filter(sql.and_(
            Segment.plan_id==self.id,
            Segment.prev_id==None,
        )).first()
        segments.append(seg)

        while seg.next:
            seg = seg.next
            segments.append(seg)

        return segments

    @hybrid_property
    def last_segment(self):
        if self.num_segments == 0:
            return None
        return Segment.query.filter(sql.and_(
            Segment.plan_id==self.id,
            Segment.next_id==None,
        )).first()

class Segment(Base):
    """
    Segment object containing both a Pace and a time in seconds, tied to an
    ActivityPlan.

    This functions as a join table which maps ActivityPlans, using a doubly
    linked list structure to enforce an ordering of Segments in an ActivityPlan.
    """
    __tablename__ = 'segments'
    query = DBSession.query_property()

    # State
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('activity_plans.id'), nullable=False)
    pace_id = Column(Integer, ForeignKey('paces.id'), nullable=False)
    length = Column(Integer, nullable=False)
    prev_id = Column(Integer, ForeignKey('segments.id'), nullable=True)
    next_id = Column(Integer, ForeignKey('segments.id'), nullable=True)

    # Relationships
    plan = relationship('ActivityPlan')
    pace = relationship('Pace')
    prev = relationship('Segment', foreign_keys='[Segment.prev_id]')
    next = relationship('Segment', foreign_keys='[Segment.next_id]')
