# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from sqlalchemy import Column, ForeignKey, Float, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///weather_map.db')
Base.metadata.bind = engine


class ParseType(Base):
    """
    """
    __tablename__ = 'parse_type'
    id = Column(Integer, primary_key=True)

class MapType(Base):
    """
    """
    __tablename__ = 'map_type'
    id = Column(Integer, primary_key=True)
    name_rus = Column(String(30), nullable=False)

class Continent(Base):
    """
    """
    __tablename__ = 'continent'
    id = Column(Integer, primary_key=True)
    name_rus = Column(String(30), nullable=False)


class Region(Base):
    """
    """
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    name_rus = Column(String(30), nullable=False)
    continent_id = Column(Integer, ForeignKey('continent.id'))
    continent = relationship(Continent)


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
    parse_type_id = Column(Integer, ForeignKey('parse_type.id'))
    parse_type = relationship(ParseType)

    bot_path = Column(String(50), nullable=False)
    info = Column(String(100))
    url = Column(String(300))

    update_delay = Column(Integer)

    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Integer)

    last_update = Column(DateTime)


    map_type_id = Column(Integer, ForeignKey('map_type.id'))
    map_type = relationship(MapType)

    region_id = Column(Integer, ForeignKey('region.id'))
    region = relationship(Region)

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

    def __str__(self):
        return "id=%d, url=%s, path=%s, time=%s, download_time=%s, map_id=%d" % \
            (self.id, self.url, self.path, self.timestamp.strftime('%d.%m.%Y %H:%M UTC'), \
                self.download_time.strftime('%d.%m.%Y %H:%M UTC'), self.map_id)

class DBSession(object):
    def __init__(self):
        self.DBSession = sessionmaker(bind=engine)

    def __enter__(self):
        self.s = self.DBSession()
        return self.s

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.commit()
        self.s.close()

