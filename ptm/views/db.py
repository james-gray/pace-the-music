# This module is used to interact with the database

from ptm.models.music import Playlist
from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.base import session

# Each key represents a pace object in the DB
paces = {'Slow':Pace.query.filter_by(speed='Slow').first(), 'Steady':Pace.query.filter_by(speed='Steady').first(), 'Fast':Pace.query.filter_by(speed='Fast').first(), 'Sprint':Pace.query.filter_by(speed='Sprint').first()}


def getPace(pid):
    pace = session.query(Pace).filter(Pace.id == pid)
    return pace[0].speed

# Get the activity plan from the DB, create it if it doesn't exist
def getPlan(pid):
    plan = session.query(ActivityPlan).filter(ActivityPlan.id == pid)
    if plan.count()==0:
        print '\n\nNo Activity Plan exists, creating new plan\n\n'
        plan = ActivityPlan(name='Plan')
        session.add(plan)
        session.commit()
        plan = session.query(ActivityPlan).filter(ActivityPlan.id == pid)

    return plan[0]

# Get the playlist from the DB, create it if it doesn't exist
def getPlaylist(plid):
    # Check if Playlist exists, create one if it doesn't
    pl = session.query(Playlist).filter(Playlist.id == plid)
    if pl.count()==0:
        print '\n\nNo Activity Playlist exists, creating new Playlist\n\n'
        pl = Playlist(name='Playlist')
        session.add(pl)
        session.commit()
        pl = session.query(Playlist).filter(Playlist.id == plid)

    return pl[0] 

# returns a list of the segments contained in the plan with id == pid
def listSegments(pid):
    sList = []
    plan = session.query(ActivityPlan).filter(ActivityPlan.id == pid)
    segments = session.query(Segment).filter(Segment.plan_id == pid)
    for i in range(segments.count()):
        if(segments[i].plan_id == pid):
            sList.append(segments[i])
    return sList

# Add segments to activity plan
def addSegment(pid, pace, time):
    plan = getPlan(pid)
    pace = paces[pace]
    plan.append_segment(pace=pace, length=time)
    session.commit()
    print "\n\nPlan segments: %s\n\n" % plan.segments

# remove segment at specified position
def removeSegment(plan_id, seg_pos):
    plan = getPlan(plan_id)
    plan.delete_segment(seg_pos)
    session.commit()

'''def updateSegTime(plan_id, seg_pos, time):
    plan = getPlan(plan_id)
    plan.update_segment(seg_pos, time=time)
    session.commit()'''
