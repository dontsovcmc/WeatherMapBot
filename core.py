# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import os
import bs4

from network import Downloader
from db import DBSession, engine, Map, Site, Storage, Legend, Base
from maps import weather_maps
from maps import GISMETEO_MAP, PICTURE_MAP, LINK_MAP
from logger import log
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_
from datetime import datetime, timedelta
from storage import file_storage

PREVIOUS_MAP = u'<<'
NEXT_MAP = u'>>'
CHANGE_SITE = u'Выбор сайта'
CHANGE_MAP = u'Выбор карты'
REFRESH = u'Обновить'

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
                      map_type=m.map_type,
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

                    map.map_type = m.map_type
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

def get_sql_site_bot_path(id):
    with DBSession() as session:
        site = session.query(Site).get(id)
        return site.bot_path

def get_sql_map_name(id):
    with DBSession() as session:
        map = session.query(Map).get(id)
        return map.name

def maps_keyboard_layout(site_id, kb):
    maps = []
    with DBSession() as session:
        for m in session.query(Map).filter(Map.site_id == site_id).all():
            maps.append(m.name)
    maps.append(CHANGE_SITE)

    def add_kb(maps):
        return [kb(m) for m in maps]
    return [add_kb(maps[x:x+3]) for x in xrange(0, len(maps), 3)]


def found_next_map_in_storage(session, sql_map, timestamp):

    tomorrow = timestamp + timedelta(hours=24)
    storage_file = session.query(Storage)\
            .filter(Storage.map_id == sql_map.id)\
            .filter(Storage.timestamp.between(timestamp, tomorrow))\
            .all()

    if not len(storage_file):
        raise NoResultFound()

    storage_file = sorted(storage_file, key=lambda sf: (sf.timestamp - datetime.now()).total_seconds())[0]
    return storage_file


def found_previous_map_in_storage(session, sql_map, timestamp):

    yesterday = timestamp - timedelta(hours=24)
    storage_file = session.query(Storage)\
            .filter(Storage.map_id == sql_map.id)\
            .filter(Storage.timestamp.between(yesterday, timestamp))\
            .all()

    if not len(storage_file):
        raise NoResultFound()

    storage_file = sorted(storage_file, key=lambda sf: (sf.timestamp - datetime.now()).total_seconds())[-1]
    return storage_file


def get_legend(map_id):

    with DBSession() as session:
        sql_map = session.query(Map).get(map_id)
        return u'Легенда доступна по ссылке: %s' % sql_map.url


def get_map(map_id, timestamp):

    with DBSession() as session:
        sql_map = session.query(Map).get(map_id)

        if not sql_map.last_update or (datetime.now() - sql_map.last_update).total_seconds() > sql_map.update_delay: # Данные устарели
            timestamp_url_list = current_map_urls(sql_map)

            sql_map.last_update = datetime.now()
            session.commit()

            if not timestamp_url_list:
                log.error('ни одной карты на странице!')
                return None, u'нет карт на странице'
            else:
                for m in timestamp_url_list:  # (timestamp, url)
                    try:
                        found = session.query(Storage).filter(and_(Storage.timestamp == m[0], Storage.map_id == sql_map.id)).all()
                        if not len(found):
                            path = file_storage.download(m[1], sql_map.id, m[0])

                            new_file = Storage(url=m[0], path=path, timestamp=m[0],
                                      download_time=datetime.now(),
                                      map_id=sql_map.id)
                            session.add(new_file)
                            session.commit()
                    except Exception, err:
                        log.error(err)
        try:
            sql_file = found_next_map_in_storage(session, sql_map, timestamp)
            return sql_file.path, get_map_info(sql_map, sql_file.timestamp)

        except NoResultFound:
            return None, u'карта отсутствует'


def current_map_urls(sql_map):
    """
    [(timestamp, url)]
    :return:
    """
    frames = []
    if sql_map.map_type == GISMETEO_MAP:

        with Downloader() as d:
            data = d.getresponse(sql_map.url)
            soup = bs4.BeautifulSoup(data, "html.parser")

        tab_i = 0
        try:
            while True:
                imgs = soup.select('.tab%s > img' % tab_i)
                if not len(imgs):
                    break
                for i in imgs:
                    date_object = datetime.strptime(i.attrs['alt'], '%d.%m.%Y %H:%M')
                    frame = date_object, 'https:' + i.attrs['title']
                    frames.append(frame)
                tab_i += 1
        except Exception, err:
            pass

    elif sql_map.map_type == PICTURE_MAP:

        return [(datetime.now(), sql_map.url)]

    return frames

def get_map_info(sql_map, timestamp):
    return u'%s\n%s\nЛегенда: /legend' % (sql_map.name, timestamp.strftime('%d.%m.%Y %H:%M'))


def get_previous_timestamp_by_path(path):
    with DBSession() as session:
        storage_file = session.query(Storage).filter(Storage.path == path).one()
        sql_map = session.query(Map).get(storage_file.map_id)
        sql_file = found_previous_map_in_storage(session, sql_map, storage_file.timestamp-timedelta(seconds=1))
        return sql_file.timestamp


def get_next_timestamp_by_path(path):
    with DBSession() as session:
        storage_file = session.query(Storage).filter(Storage.path == path).one()
        sql_map = session.query(Map).get(storage_file.map_id)
        sql_file = found_next_map_in_storage(session, sql_map, storage_file.timestamp+timedelta(seconds=1))
        return sql_file.timestamp
