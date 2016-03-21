from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from ptm.models.base import Base
from ptm.models.base import PtmBase

class Pace(Base, PtmBase):
    """
    Pace object to be used in a Segment. One of: Slow, Steady, Fast, Sprint.
    """
    __tablename__ = 'paces'

    # State
    speed = Column(String, nullable=False)

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
