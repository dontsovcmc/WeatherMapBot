# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import bs4

from network import Downloader
from db import DBSession, Map, Site, Storage, MapType, Continent, Region
from logger import log
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_
from datetime import datetime, timedelta
from storage import file_storage
from maps import eparsetype


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

def get_continent_name_id():
    with DBSession() as session:
        return [(obj.name_rus, obj.id) for obj in session.query(Continent).all()]

def get_region_name_id():
    with DBSession() as session:
        return [(obj.name_rus, obj.id) for obj in session.query(Region).all()]

def get_type_name_id():
    with DBSession() as session:
        return [(obj.name_rus, obj.id) for obj in session.query(MapType).all()]

def get_site_id(bot_path):
    with DBSession() as session:
        site = session.query(Site).filter(Site.bot_path == bot_path).one()
        return site.id

def get_continent_name(id):
    with DBSession() as session:
        obj = session.query(Continent).get(id)
        return obj.name_rus

def get_region_name(id):
    with DBSession() as session:
        obj = session.query(Region).get(id)
        return obj.name_rus

def get_map_type_name(id):
    with DBSession() as session:
        obj = session.query(MapType).get(id)
        return obj.name_rus


def get_continent_id(name):
    with DBSession() as session:
        return session.query(Continent).filter(Continent.name_rus == name).one().id

def get_region_id(name):
    with DBSession() as session:
        return session.query(Region).filter(Region.name_rus == name).one().id

def get_map_type_id(name):
    with DBSession() as session:
        return session.query(MapType).filter(MapType.name_rus == name).one().id

def get_map_id(region_id, map_type_id):
    with DBSession() as session:
        return session.query(Map).filter(
            and_(Map.region_id == region_id, Map.map_type_id == map_type_id)).one().id


def format_sql_map_name(sql_region, sql_map_type):
    return "%s:%s" % (sql_region.name_rus, sql_map_type.name_rus)


def continent_keyboard_layout(kb):
    cont = []
    with DBSession() as session:
        sql_cont = session.query(Continent).all()
        for c in sql_cont:
            cont.append(c.name_rus)

    def add_kb(maps):
        return [kb(m) for m in maps]
    return [add_kb(cont[x:x+3]) for x in xrange(0, len(cont), 3)]


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

def add_urls_to_storage(session, map_id, timestamp_url_list):

    for m in timestamp_url_list:  # (timestamp, url)
        try:
            found = session.query(Storage).filter(and_(Storage.timestamp == m[0], Storage.map_id == map_id)).all()
            if not len(found):
                path = file_storage.download(m[1], map_id, m[0])

                new_file = Storage(url=m[1], path=path, timestamp=m[0],
                          download_time=datetime.now(),
                          map_id=map_id)
                session.add(new_file)
                session.commit()
        except Exception, err:
            log.error(err)


def get_map(map_id, timestamp):

    with DBSession() as session:
        sql_map = session.query(Map).get(map_id)

        if not sql_map.last_update or (datetime.now() - sql_map.last_update).total_seconds() > sql_map.update_delay / 2: # Данные устарели
            timestamp_url_list = current_map_urls(sql_map)

            sql_map.last_update = datetime.now()
            session.commit()

            if not timestamp_url_list:
                log.error('ни одной карты на странице!')
                return None, u'нет карт на странице'
            else:
                add_urls_to_storage(session, sql_map.id, timestamp_url_list)
        try:
            sql_file = found_next_map_in_storage(session, sql_map, timestamp)
            return sql_file.path, get_map_info(session, sql_map, sql_file.timestamp)

        except NoResultFound:
            # нет будущих карт. вернем предыдущую, если она моложе времени предыдущего обновления
            try:
                sql_file = found_next_map_in_storage(session, sql_map, timestamp-timedelta(seconds=sql_map.update_delay))
                return sql_file.path, get_map_info(session, sql_map, sql_file.timestamp)

            except NoResultFound:
                return None, u'карта отсутствует'


def current_map_urls(sql_map):
    """
    [(timestamp, url)]
    :return:
    """
    frames = []
    if sql_map.parse_type_id == eparsetype.GISMETEO_MAP:

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

    elif sql_map.parse_type_id == eparsetype.PICTURE_MAP:

        frames.append((datetime.now(), sql_map.url))

    return frames

def get_map_info(session, sql_map, timestamp):
    sql_map_type = session.query(MapType).get(sql_map.map_type_id)
    sql_region = session.query(Region).get(sql_map.region_id)
    return u'%s:%s\n%s\nЛегенда: /legend' % (sql_region.name_rus, sql_map_type.name_rus,
                                          timestamp.strftime('%d.%m.%Y %H:%M'))


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
