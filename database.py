#!/usr/bin/env python
import argparse
import os
import subprocess
import sys

import sqlalchemy

from ptm.models.base import Base
from ptm.models.base import engine

# XXX: You'll notice that these model imports are never actually 'used', in the
# traditional sense. Don't delete them or you're gonna have a bad time!
#
# SQLAlchemy has this stupid 'feature' that requires you to import the classes
# if you define them in a different module than where you are creating them,
# or else `Base.metadata.create_all()` won't 'see' them and as a result won't
# create the necessary tables. I'm not entirely sure why, but to appease the
# SQLAlchemy gods I've left these here.
# See http://stackoverflow.com/questions/20744277/sqlalchemy-create-all-does-not-create-tables
from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.activity import Segment
from ptm.models.base import session
from ptm.models.music import Artist
from ptm.models.music import Song
from ptm.models.music import SongMeta

from config import db

parser = argparse.ArgumentParser(description='Database helper functions')
parser.add_argument('action', help='One of: `create`, `drop`')

def setup_database():
    '''
    Create the database and its tables.
    '''
    print 'Creating tables...'
    try:
        Base.metadata.create_all(engine)

        # Create Pace objects
        for pace in ['Slow', 'Steady', 'Fast', 'Sprint']:
            session.add(Pace(speed=pace))
        session.commit()
    except:
        raise
    else:
        print 'Tables created successfully.'

def drop_database():
    '''
    Delete the database permanently.
    WARNING: This deletes the database permanently!
    '''
    print 'You are about to delete the "%s" database permanently! Are you sure? [Y/n] ' % db['path'],
    choice = raw_input().lower()
    if choice == 'y':
        try:
            Base.metadata.drop_all(engine)
            os.remove(db['path'])
        except sqlalchemy.exc.InternalError:
            raise
        else:
            print 'Database deleted successfully.'

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])

    if args.action == 'create':
        setup_database()
    elif args.action == 'drop':
        drop_database()
    else:
        print 'ERROR: You must specify which command you wish to execute: one of (create, drop).'
