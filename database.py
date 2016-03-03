#!/usr/bin/env python3
import argparse
import subprocess
import sys

import sqlalchemy
from sqlalchemy import create_engine

from model import Base

from config import db

parser = argparse.ArgumentParser(description='Database helper functions')
parser.add_argument('action', help='One of: `create`, `drop`')

# TODO: Ditch MySQL and sqitch to a SQLite database
# It doesn't really make sense to require the (theoretical) user to have
# MySQL installed (a complicated and large thing to do) in order to use this
# utility
engine = create_engine('mysql+pymysql://%s:%s@%s/%s' \
    % (db['user'], db['pass'], db['host'], db['name']))

def setup_database():
    '''
    Create the database and its tables.
    '''
    print('Creating database %s...' % db['name'])

    try:
        args = [
            'mysql',
            '-u%s' % db['user'],
            '-p%s' % db['pass'],
            '-e', 'CREATE DATABASE IF NOT EXISTS %s;' % db['name'],
        ]
        print(args)
        subprocess.check_call(args)
    except subprocess.CalledProcessError:
        raise
    else:
        print('Database created successfully.')

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
        % db['name'], end='')
    choice = input().lower()
    if choice == 'y':
        conn = engine.connect()
        try:
            conn.execute('DROP DATABASE %s' % db['name'])
        except sqlalchemy.exc.InternalError:
            raise
        else:
            print('Database deleted successfully.')
        conn.close()

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])

    if args.action == 'create':
        setup_database()
    elif args.action == 'drop':
        drop_database()
    else:
        print('ERROR: You must specify which command you wish to execute: one of (create, drop).')
