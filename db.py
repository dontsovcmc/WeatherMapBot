# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///weather_map.db')
Base.metadata.bind = engine

class Legend(Base):
    """

    """
    __tablename__ = 'legend'

    id = Column(Integer, primary_key=True)
    info = Column(String(50))


class Site(Base):
    '''
    Сайты
    '''
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True)
    url = Column(String(100), nullable=False)
    bot_path = Column(String(100), nullable=False)


class Map(Base):
    '''
    Различные карты
    '''
    __tablename__ = 'map'

    id = Column(Integer, primary_key=True)
    map_type = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    bot_path = Column(String(50), nullable=False)
    info = Column(String(100))
    url = Column(String(300))
    update_delay = Column(Integer)
    last_update = Column(DateTime)
    region = Column(String(50))
    mtype = Column(String(50))

    legend_id = Column(Integer, ForeignKey('legend.id'))
    legend = relationship(Legend)

    site_id = Column(Integer, ForeignKey('site.id'))
    site = relationship(Site)


class Storage(Base):
    '''
    Хранилище карт на диске
    '''
    __tablename__ = 'storage'

    id = Column(Integer, primary_key=True)
    url = Column(String(300))
    path = Column(String(300))
    timestamp = Column(DateTime)
    download_time = Column(DateTime)

    temperature = Column(Integer)
    wind = Column(Integer)
    wind_direction = Column(Integer)
    pressure = Column(Integer)

    map_id = Column(Integer, ForeignKey('map.id'))
    map = relationship(Map)


class DBSession(object):
    def __init__(self):
        self.DBSession = sessionmaker(bind=engine)

    def __enter__(self):
        self.s = self.DBSession()
        return self.s

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.commit()
        self.s.close()

