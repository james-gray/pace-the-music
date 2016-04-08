from ptm.models.music import Playlist
from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.base import session

# Each key represents a pace object in the DB
paces = {'Slow':Pace.query.filter_by(speed='Slow').first(), 'Steady':Pace.query.filter_by(speed='Steady').first(), 'Fast':Pace.query.filter_by(speed='Fast').first(), 'Sprint':Pace.query.filter_by(speed='Sprint').first()}
class DatabaseFunctions:

    # Get the activity plan from the DB, create it if it doesn't exist
    def getPlan(self):
        plan = session.query(ActivityPlan).filter(ActivityPlan.id == 1)
        if plan.count()>0:
            print '\n\nPlan exists\n\n'
        else:
            print '\n\nNo Activity Plan exists, creating new plan\n\n'
            plan = ActivityPlan(name='Plan')
            session.add(plan)
            session.commit()
            plan = session.query(ActivityPlan).filter(ActivityPlan.name == 'Plan')
        return plan[0]

    # Get the playlist from the DB, create it if it doesn't exist
    def getPlaylist(self):

        #TODO

        # Check if Playlist exists, create one if it doesn't
        pl = session.query(Playlist).filter(Playlist.id == 1)
        if pl.count()>0:
            print '\n\nPlaylist exists\n\n'
        else:
             print '\n\nNo Activity Playlist exists, creating new Playlist\n\n'
            pl = Playlist(name='Playlist')
            session.add(pl)
            session.commit()
            plan = session.query(Playlist).filter(ActivityPlan.name == 'Plan')
        return plan[0] 

    # Add segments to activity plan
    def addSegment(self, plan, pace, time):
        pace = paces[pace]
        plan.append_segment(pace=pace, length=time)
        session.commit()
        print "\n\nPlan segments: %s\n\n" % plan.segments