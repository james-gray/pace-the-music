# This module is used to interact with the database

from ptm.models.music import Playlist
from ptm.models.music import Song
from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.base import session

# Each key represents a pace object in the DB
paces = {
    'Slow': Pace.query.filter_by(speed='Slow').first(),
    'Steady': Pace.query.filter_by(speed='Steady').first(),
    'Fast': Pace.query.filter_by(speed='Fast').first(),
    'Sprint': Pace.query.filter_by(speed='Sprint').first(),
}


def getPace(pace_id):
    pace = session.query(Pace).filter(Pace.id == pace_id)
    return pace[0].speed


# Get the activity plan from the DB, create it if it doesn't exist
def getPlan(plan_id):
    plan = ActivityPlan.query.filter(ActivityPlan.id == plan_id).first()
    if not plan:
        print '\nNo Activity Plan exists, creating new plan\n'
        plan = ActivityPlan(name='Plan')
        session.add(plan)
        session.commit()

    return plan


# Get the playlist from the DB, create it if it doesn't exist
def getPlayList(playlist_id):
    # Check if Playlist exists, create one if it doesn't
    playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
    if not playlist:
        print '\nNo Activity Playlist exists, creating new Playlist\n'
        playlist = Playlist(name='Playlist')
        session.add(playlist)
        session.commit()

    return playlist


# this is where the magic happens
def generatePlayList(playlist_id, plan_id):
    songs = Song.query.all()
    if not songs: # make sure there are songs in the database
        print '\nNo songs available\n'
        #TODO: possibly add the songs?
        return

    playlist = getPlayList(playlist_id)
    plan = getPlan(plan_id)
    playlist.generate(plan)
    session.commit()


# returns a list of the segments contained in the plan with id == plan_id
def listSegments(plan_id):
    segment_list = []
    segments = Segment.query.filter(Segment.plan_id == plan_id)
    for i in range(segments.count()):
        if(segments[i].plan_id == plan_id):
            segment_list.append(segments[i])
    return segment_list


# Add segments to activity plan
def addSegment(plan_id, pace, time):
    plan = getPlan(plan_id)
    pace = paces[pace]
    plan.append_segment(pace=pace, length=time)
    session.commit()
    print "\nPlan segments: %s\n" % plan.segments


# remove segment at specified position
def removeSegment(plan_id, seg_pos):
    plan = getPlan(plan_id)
    plan.delete_segment(seg_pos)
    session.commit()


# update the lenth of a segment in the database
def updateSegTime(plan_id, seg_pos, time):
    plan = getPlan(plan_id)
    plan.update_segment(position=seg_pos, length=time)
    session.commit()


# update the pace of a segment in the database
def updateSegPace(plan_id, seg_pos, pace):
    plan = getPlan(plan_id)
    pace = paces[pace]
    plan.update_segment(position=seg_pos, pace=pace)
    session.commit()
