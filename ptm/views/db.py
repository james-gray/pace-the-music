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
    plan = session.query(ActivityPlan).filter(ActivityPlan.id == plan_id)
    if plan.count()==0:
        print '\nNo Activity Plan exists, creating new plan\n'
        plan = ActivityPlan(name='Plan')
        session.add(plan)
        session.commit()
        plan = session.query(ActivityPlan).filter(ActivityPlan.id == plan_id)

    return plan[0]

# Get the playlist from the DB, create it if it doesn't exist
def getPlayList(playlist_id):
    # Check if Playlist exists, create one if it doesn't
    playlist = session.query(Playlist).filter(Playlist.id == playlist_id)
    if playlist.count()==0:
        print '\nNo Activity Playlist exists, creating new Playlist\n'
        playlist = Playlist(name='Playlist')
        session.add(playlist)
        session.commit()
        playlist = session.query(Playlist).filter(Playlist.id == playlist_id)

    return playlist[0]

# this is where the magic happens
def generatePlayList(playlist_id, plan_id):
    song = session.query(Song)
    if(song.count()==0): # make sure there are songs in the database
        print '\nNo songs available\n'
        #TODO: possibly add the songs?
        return

    playList = getPlayList(playlist_id)
    plan = getPlan(plan_id)
    playList.generate(plan)


# returns a list of the segments contained in the plan with id == plan_id
def listSegments(plan_id):
    segment_list = []
    segments = session.query(Segment).filter(Segment.plan_id == plan_id)
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
