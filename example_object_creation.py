#!/usr/bin/env python
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from model import Artist
from model import Song
from model import engine

Session = sessionmaker(bind=engine)

def main():
    # Create the database session.
    # TODO: Figure out a better way to reuse the session throughout our code
    session = Session()

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

    session.commit()

    print "Artists: %s, %s" % (kanye, mozart)
    print "Each artist's songs: Kanye: %s, Mozart: %s" % (kanye.songs, mozart.songs)

if __name__ == '__main__':
    main()
