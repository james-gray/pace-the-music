#!/usr/bin/env python
from datetime import datetime

from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.music import Artist
from ptm.models.music import Playlist
from ptm.models.music import Song
from ptm.models.base import session

def music_example():
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

    # Create a playlist
    playlist = Playlist(name='test')
    session.add(playlist)
    session.flush()

    # Add some songs to the playlist
    playlist.append_song(stronger)
    playlist.append_song(love_lockdown)
    playlist.append_song(requiem)

    # Delete a song from the playlist
    playlist.delete_song(1)

    # Insert a song at number 3 in the playlist
    playlist.insert_song(2, love_lockdown)

    session.commit()

    print "Artists: %s, %s" % (kanye, mozart)
    print "Each artist's songs: Kanye: %s, Mozart: %s" % (kanye.songs, mozart.songs)
    print "Playlist songs: %s" % playlist.songs

def activity_example():
    # Create pace objects and add to session
    slow, steady, fast, sprint = Pace(speed='Slow'), Pace(speed='Steady'), \
        Pace(speed='Fast'), Pace(speed='Sprint')

    session.add(slow)
    session.add(steady)
    session.add(fast)
    session.add(sprint)

    # Create an activity plan
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

    # Clean up orphaned segments
    Segment.remove_orphans()

    session.commit()

    print "Plan segments: %s" % plan.segments

def main():
    # Create pace objects and add to session
    slow, steady, fast, sprint = Pace(speed='Slow'), Pace(speed='Steady'), \
        Pace(speed='Fast'), Pace(speed='Sprint')

    session.add(slow)
    session.add(steady)
    session.add(fast)
    session.add(sprint)

    # Create an activity plan
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

    # Clean up orphaned segments
    Segment.remove_orphans()

    session.commit()

    print "Plan segments: %s" % plan.segments

if __name__ == '__main__':
    music_example()
    activity_example()
