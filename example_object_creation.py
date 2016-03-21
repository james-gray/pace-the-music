#!/usr/bin/env python
from datetime import datetime

from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.music import Artist
from ptm.models.music import Song
from ptm.models.base import DBSession

def main():
    # Create the database session.
    session = DBSession()

    # Create artists
    kanye = Artist(name='Kanye West')
    mozart = Artist(name='Wolfgang Amadeus Mozart')

    # Add artists to the DB session and flush to generate their primary key IDs
    session.add(kanye)
    session.add(mozart)
    session.flush()

    # Create songs
    stronger = Song(
        filename='stronger.mp3',
        title='Stronger',
        date_added=datetime.utcnow(),
        artist=kanye, # Assign the artist object directly
    )
    love_lockdown = Song(
        filename='love_lockdown.mp3',
        title='Love Lockdown',
        date_added=datetime.utcnow(),
        artist=kanye,
    )

    requiem = Song(
        filename='requiem.mp3',
        title='Requiem',
        date_added=datetime.utcnow(),
        artist=mozart,
    )

    # Add songs to the DB session and flush to generate their primary key IDs
    # as well as populating the artist_id field
    session.add(stronger)
    session.add(love_lockdown)
    session.add(requiem)
    session.flush()

    slow, steady, fast, sprint = Pace(speed='Slow'), Pace(speed='Steady'), \
        Pace(speed='Fast'), Pace(speed='Sprint')

    session.add(slow)
    session.add(steady)
    session.add(fast)
    session.add(sprint)

    plan = ActivityPlan(name='test')
    session.add(plan)
    session.flush()

    plan.segments.append(Segment(pace=slow, length=60))
    plan.segments.append(Segment(pace=steady, length=60))
    plan.segments.append(Segment(pace=fast, length=60))
    plan.segments.append(Segment(pace=sprint, length=60))

    print "Artists: %s, %s" % (kanye, mozart)
    print "Each artist's songs: Kanye: %s, Mozart: %s" % (kanye.songs, mozart.songs)

if __name__ == '__main__':
    main()
