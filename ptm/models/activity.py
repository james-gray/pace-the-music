from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from ptm.models.base import Base
from ptm.models.base import PtmBase
from ptm.models.base import session

class Pace(Base, PtmBase):
    """
    Pace object to be used in a Segment. One of: Slow, Steady, Fast, Sprint.
    """
    __tablename__ = 'paces'

    # State
    speed = Column(String, nullable=False)

    # Behaviour
    def __repr__(self):
        return '<Pace(speed="%s")>' % self.speed

class ActivityPlan(Base, PtmBase):
    """
    Named activity plan object which will be associated with several Segments
    via the plans_segments join table.
    """
    __tablename__ = 'activity_plans'

    # State
    name = Column(String, nullable=False) # User-specified plan name (e.g. "HIIT Run")

    # Relationships
    segments = relationship('Segment', order_by='Segment.position',
                            collection_class=ordering_list('position'))

    # Behaviour
    def __repr__(self):
        return '<ActivityPlan(name="%s")>' % self.name

    def append_segment(self, pace, length):
        """
        Append a segment to the list with pace `pace` and length `length`.
        """
        self.segments.append(Segment(pace=pace, length=length))

    def insert_segment(self, position, pace, length):
        """
        Insert a segment with pace `pace` and length `length` at position
        `position`.
        """
        self.segments.insert(position, Segment(pace=pace, length=length))

    def update_segment(self, position, pace=None, length=None):
        """
        Update the segment at position `position` with pace `pace` and/or
        length `length`.
        """
        if not (pace or length):
            # noop
            return

        segment = self.segments[position]
        segment.pace = pace or segment.pace
        segment.length = length or segment.length
        self.segments[position] = segment

    def delete_segment(self, position):
        """
        Delete the segment at position `position` and ensure the deleted segment
        is purged from the database.
        """
        seg = self.segments.pop(position)
        session.flush()
        session.delete(seg)

class Segment(Base, PtmBase):
    """
    Segment object containing both a Pace and a time in seconds, tied to an
    ActivityPlan.

    This functions as a join table which maps ActivityPlans, using a doubly
    linked list structure to enforce an ordering of Segments in an ActivityPlan.
    """
    __tablename__ = 'segments'

    # State
    plan_id = Column(Integer, ForeignKey('activity_plans.id'), nullable=False)
    pace_id = Column(Integer, ForeignKey('paces.id'), nullable=False)
    position = Column(Integer)
    length = Column(Integer, nullable=False)

    # Relationships
    plan = relationship('ActivityPlan')
    pace = relationship('Pace')

    # Behaviour
    def __repr__(self):
        return '<Segment(pace="%s", length=%d)>' % (
            self.pace.speed,
            self.length,
        )

    @classmethod
    def remove_orphans(cls):
        """
        Remove 'orphaned' segments (i.e. segments with no plan.)

        Ideally this won't need to be used if you only add/remove segments using
        methods of ActivityPlan, however if for whatever reason you end up with
        orphans you can use this method.
        """
        cls.query.filter(cls.plan_id == None).delete(synchronize_session='fetch')
