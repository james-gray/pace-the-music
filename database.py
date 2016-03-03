#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

import sqlalchemy
from sqlalchemy import create_engine

from model import Base

from config import db

parser = argparse.ArgumentParser(description='Database helper functions')
parser.add_argument('action', help='One of: `create`, `drop`')

engine = create_engine('sqlite:///%s' % db['path'], echo=True)

def setup_database():
    '''
    Create the database and its tables.
    '''
    print('Creating database %s...' % db['path'])

    print('Creating tables...')
    try:
        Base.metadata.create_all(engine)
    except:
        raise
    else:
        print('Tables created successfully.')

def drop_database():
    '''
    Delete the database permanently.
    WARNING: This deletes the database permanently!
    '''
    print('You are about to delete the "%s" database permanently! Are you sure? [Y/n] ' \
        % db['path'], end='')
    choice = input().lower()
    if choice == 'y':
        try:
            Base.metadata.drop_all(engine)
            os.remove(db['path'])
        except sqlalchemy.exc.InternalError:
            raise
        else:
            print('Database deleted successfully.')

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])

    if args.action == 'create':
        setup_database()
    elif args.action == 'drop':
        drop_database()
    else:
        print('ERROR: You must specify which command you wish to execute: one of (create, drop).')
