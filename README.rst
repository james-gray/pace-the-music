==============
Pace the Music
==============

Prerequisites
=============

Pace the Music requires Python 3.5, MySQL 5.7 and PIP v8.0.3.

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

To set up the database you will need to make sure that you have MySQL 5.7 installed.
After installing MySQL, ensure you have created a root database user::

   mysql> CREATE USER 'root'@'localhost' IDENTIFIED BY 'some_password';

Next, copy `config_template.py` to the file `config.py` and edit the DB host, user,
and password strings accordingly to match the new user. Finally, create the DB and tables::

   $ ./database.py create

If for some reason you want to delete your database and start from scratch, run the following command::

   $ ./database.py drop
