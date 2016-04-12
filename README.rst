==============
PaceTheMusic
==============

Prerequisites
=============

PaceTheMusic is cross platform, but requires the following programs and utilities to install and run:

 - Python 2.7
 - SQLite 3
 - PIP v8.0.3
 - Qt 5
 - PyQt5
 
Bundled in this repository are the requisite PyQt5 modules, but you will need to install the Qt 5 framework before the application will run. See http://www.qt.io/download/ for detailed download and installation instructions.

Installing PaceTheMusic
=========================

Install dependencies using the following command::

   $ pip install -r requirements.txt

To set up the database you will need to make sure that you have SQLite 3 installed.

Next, copy ``config_template.py`` to the file ``config.py`` and set the path to ``'ptm.db'``. Additionally you can reduce the verbosity of database engine output to the command line by changing the ``'verbose'`` directive in ``config.py`` from ``True`` to ``False``.

Finally, set up the application. The following command will create the DB and tables, download the ``music_repo.tar`` corpus, unzip it to the ``corpus`` directory, and populate the database with the music metadata::

   $ ./setup_app.py

You can also simply create the database alone, without performing the additional setup, with the following command::

   $ ./database.py create

If for some reason you want to delete your database and start from scratch, run the following command::

   $ ./database.py drop
   
Running PaceTheMusic
====================

To start the main program execution loop simply run the following command::

   $ ./app.py
   
If you have installed the dependencies correctly the main app window should open.

Upgrading requirements
======================

If the requirements have changed or you need to update them for some reason run the following command::

   $ pip install -U -r requirements.txt
