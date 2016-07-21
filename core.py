# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import os
from db import DBSession, engine, Map, Site, Storage, Legend, Base
from maps import weather_maps
from logging import log
from sqlalchemy.orm.exc import NoResultFound

CHANGE_SITE = u'Выбор сайта'

def init():

    def get_sql_site(session, weather_map):
        url = weather_map.url.split('//')[1].split('/')[0]
        try:
            sql_site = session.query(Site).filter(Site.url==url).one()
        except NoResultFound, err:
            bot_path = url.replace('.','_')
            sql_site = Site(url=url,bot_path=bot_path)
            session.add(sql_site)
        return sql_site

    def get_sql_legend(session, weather_map):
        try:
            sql_legend = session.query(Legend).filter(Legend.info==weather_map.legend).one()
        except NoResultFound, err:
            sql_legend = Legend(info=weather_map.legend)
            session.add(sql_legend)
        return sql_legend

    def add_new_map(session, m):

        sql_site = get_sql_site(session, m)
        sql_legend = get_sql_legend(session, m)

        new_map = Map(name=m.name,
                      bot_path=m.bot_path,
                      info=m.info, url=m.url,
                      update_delay=m.update_delay, region=m.region,
                      mtype=m.mtype,
                      legend_id=sql_legend.id,
                      site_id=sql_site.id)
        session.add(new_map)


    if not os.path.isfile('weather_map.db'):
        Base.metadata.create_all(engine)

        #create
        with DBSession() as session:

            try:
                for m in weather_maps:
                    add_new_map(session, m)

            except Exception, err:
                log.error(err)

    else:
        #update
        with DBSession() as session:
            for m in weather_maps:
                try:
                    map = session.query(Map).filter(Map.name == m.name).one()

                    sql_site = get_sql_site(session, m)
                    sql_legend = get_sql_legend(session, m)

                    map.bot_path = m.bot_path
                    map.info = m.info
                    map.url = m.url
                    map.update_delay = m.update_delay
                    map.region = m.region
                    map.mtype = m.mtype
                    map.legend_id = sql_legend.id
                    map.site_id = sql_site.id

                except NoResultFound, err:
                    add_new_map(session, m)

                except Exception, err:
                    log.error(err)


def add_map_to_storage(map_id, url, path, timestamp, download_time):
    with DBSession() as session:
        new_file = Storage(url=url, path=path, timestamp=timestamp,
                          download_time=download_time,
                          map_id=map_id)
        session.add(new_file)


def sites_keyboard_layout(kb):
    '''
    :param kb:
    :return:
    '''
    sites = []
    with DBSession() as session:
        for s in session.query(Site).all():
            sites.append(s.bot_path)

    def add_kb(sites):
        return [kb(s) for s in sites]

    return [add_kb(sites[x:x+3]) for x in xrange(0, len(sites), 3)]


def get_site_id(bot_path):
    with DBSession() as session:
        site = session.query(Site).filter(Site.bot_path == bot_path).one()
        return site.id


def get_sql_map_id(name):
    with DBSession() as session:
        map = session.query(Map).filter(Map.name == name).one()
        return map.id

def get_sql_map(map_id):
    with DBSession() as session:
        return session.query(Map).get(map_id)

def maps_keyboard_layout(site_id, kb):
    maps = []
    with DBSession() as session:
        for m in session.query(Map).filter(Map.site_id == site_id).all():
            maps.append(m.name)
    maps.append(CHANGE_SITE)

    def add_kb(maps):
        return [kb(m) for m in maps]
    return [add_kb(maps[x:x+3]) for x in xrange(0, len(maps), 3)]

