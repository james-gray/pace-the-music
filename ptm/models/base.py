from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer

from config import db

engine = create_engine('sqlite:///%s' % db['path'], echo=True)
DBSession = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class PtmBase(object):
    """
    Base mixin that can be used as a subclass in model objects. If you notice
    that you're adding identical stuff to each model class you should add it here
    instead!

    See http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/mixins.html
    """
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
