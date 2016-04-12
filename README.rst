==============
Pace the Music
==============

Prerequisites
=============

Pace the Music requires Python 2.7, SQLite 3 and PIP v8.0.3.

Installing Pace the Music
=========================

Install dependencies using the following command::

   $ pip install -r requirements.txt

Upgrading requirements
======================

If the requirements have changed or you need to update them for some reason run the following command::

   $ pip install -U -r requirements.txt

Setting up the app
==================

To set up the database you will need to make sure that you have SQLite 3 installed.

Next, copy `config_template.py` to the file `config.py` and set the path to 'ptm.db'. Finally, set up the application. The following command will create the DB and tables, download the `music_repo.tar` corpus, unzip it to the `corpus` directory, and populate the database with the music metadata::

   $ ./setup_app.py

You can also simply create the database alone, without performing the additional setup, with the following command::

   $ ./database.py create

If for some reason you want to delete your database and start from scratch, run the following command::

   $ ./database.py drop
