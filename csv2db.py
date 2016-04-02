#!/usr/bin/env python
from datetime import datetime

from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.music import Artist
from ptm.models.music import Playlist
from ptm.models.music import Song
from ptm.models.music import SongMeta
from ptm.models.base import session
import csv

# ./database.py create
# ./database.py drop

def music_example():
   csvfile = open('song_dict.csv', 'r')
   csvreader = csv.reader(csvfile, delimiter=',', quotechar = '\"')
   for song in csvreader:
	# Create artists
        artist_name = unicode(song[1])
        art = Artist.query.filter_by(name=artist_name).first()
	if not art:
           # Create new artist
	   art = Artist(name=unicode(song[1]))
	   # Add artists to the DB session and flush to generate their
	   # primary key IDs
	   session.add(art)
	   session.flush()

	# Create songs
	song2add = Song(
	   filename='booo',
	   title=str(song[0]),
	   date_added=datetime.utcnow(),
	   artist=art, # Assign the artist object directly
	)

	# Add songs to the DB session and flush to generate their
	# primary key IDs as well as populating the artist_id field
	session.add(song2add)
	session.flush()

	# Create Metadata
	meta = SongMeta(
	   duration = int(float(song[3])),
	   bpm = int(song[2]),
	   song = song2add
	)
	session.add(meta)
	session.flush() 
   session.commit()	

if __name__ == '__main__':
    music_example()
