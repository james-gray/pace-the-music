#!/usr/bin/env python
from datetime import datetime

from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.music import Artist
from ptm.models.music import Song
from ptm.models.base import session

def main():
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

    # Add 4 segments to the plan
    plan.append_segment(pace=steady, length=60)
    plan.append_segment(pace=steady, length=60)
    plan.append_segment(pace=slow, length=10)
    plan.append_segment(pace=sprint, length=60)

    # Whoops - I made a mistake and want to delete a segment!
    plan.delete_segment(1)

    # Fix the second segment
    plan.update_segment(position=1, pace=fast, length=60)

    # Add a segment to the beginning
    plan.insert_segment(position=0, pace=slow, length=60)

    session.commit()

    print "Artists: %s, %s" % (kanye, mozart)
    print "Each artist's songs: Kanye: %s, Mozart: %s" % (kanye.songs, mozart.songs)
    print "Plan segments: %s" % plan.segments


if __name__ == '__main__':
    main()
