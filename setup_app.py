#!/usr/bin/env python
import csv
import os
import subprocess

from datetime import datetime

from database import drop_database
from database import setup_database
from ptm.models.base import session
from ptm.models.music import Artist
from ptm.models.music import Song
from ptm.models.music import SongMeta

corpus_location = 'http://www.reynolds-theatre.com/content/music_repo.tar'

def csv_import():
    print "Importing CSV song data into the database..."
    csvfile = open('song_dict.csv', 'r')
    csvreader = csv.reader(csvfile, delimiter=',', quotechar = '\"')
    artist_dict = {}
    for title, artist_name, bpm, duration, filename in csvreader:
        # Create or fetch artist
        artist_name = artist_name.decode('utf-8')
        artist = artist_dict.get(artist_name)
        if not artist:
            # Create new artist
            artist = Artist(name=artist_name)

            # Add artists to the DB session and flush to generate their
            # primary key IDs
            session.add(artist)
            session.flush()

            # Remember the artist via the artists dict
            artist_dict[artist_name] = artist

        # Create songs
        song = Song(
            filename = os.path.abspath(filename.decode('utf-8')),
            title = title.decode('utf-8'),
            date_added = datetime.utcnow(),
            artist = artist, # Assign the artist object directly
        )

        # Add songs to the DB session and flush to generate their
        # primary key IDs as well as populating the artist_id field
        print "Adding song %s..." % song
        session.add(song)
        session.flush()

        # Create Metadata
        meta = SongMeta(
            duration = int(float(duration)),
            bpm = int(bpm),
            song = song,
        )
        session.add(meta)
        session.flush()

    session.commit()
    print "CSV import finished successfully."

def download_corpus():
    corpus_path = './corpus'
    if not os.path.exists(corpus_path):
        os.mkdir(corpus_path, 0755)

    print "Downloading corpus..."
    if not os.path.exists('./corpus/music_repo.tar'):
        # Download the music corpus from James's cheap VPS that he's hosting it on
        subprocess.check_call([
            'wget',
            corpus_location,
            '-P',
            corpus_path,
        ])
    else:
        print "Corpus already downloaded, skipping."

    print "Unzipping songs..."
    if len(os.listdir(corpus_path)) > 1:
        print "Songs already unzipped, skipping."
    else:
        subprocess.check_call([
            'tar',
            '-xzf',
            './corpus/music_repo.tar',
            '-C',
            corpus_path,
        ])
        print "Successfully unzipped songs."

if __name__ == '__main__':
    print "Dropping existing database..."
    drop_database()
    print "Setting up the database..."
    setup_database()
    print "Finished database setup.\n"
    download_corpus()
    csv_import()
