# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from db import DBSession, Map, Site, Storage, MapType, Continent, Region
from logger import log
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from storage import file_storage
from parsers import current_map_urls
from math import radians, cos, sin, asin, sqrt


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

def get_map_type_id():
    with DBSession() as session:
        return [(obj.name_rus, obj.id) for obj in session.query(MapType).all()]

def filter_region_name(cont_id):
    with DBSession() as session:
        return [obj.name_rus for obj in session.query(Region).filter(Region.continent_id == cont_id)]

def filter_type_name(region_id):
    """
    Показываем типы карт, которые есть у выбранного региона
    :param region_id:
    :return:
    """
    with DBSession() as session:
        mtypes = [obj.map_type_id for obj in session.query(Map).filter(Map.region_id == region_id)]
        return [obj.name_rus for obj in session.query(MapType).filter(MapType.id.in_(mtypes)).all()]


def get_region_type_by_map_id(id):
    with DBSession() as session:
        sql_map = session.query(Map).get(id)
        region = session.query(Region).get(sql_map.region_id)
        mtype = session.query(MapType).get(sql_map.map_type_id)
        return region.name_rus, mtype.name_rus

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
        return None

    storage_file = sorted(storage_file, key=lambda sf: (sf.timestamp - datetime.utcnow()).total_seconds())[0]
    return storage_file


def found_previous_map_in_storage(session, sql_map, timestamp):

    yesterday = timestamp - timedelta(hours=24)
    storage_file = session.query(Storage)\
            .filter(Storage.map_id == sql_map.id)\
            .filter(Storage.timestamp.between(yesterday, timestamp))\
            .all()

    if not len(storage_file):
        return None

    storage_file = sorted(storage_file, key=lambda sf: (sf.timestamp - datetime.utcnow()).total_seconds())[-1]
    return storage_file


def get_legend(map_id):

    with DBSession() as session:
        sql_map = session.query(Map).get(map_id)
        return u'Легенда доступна по ссылке: %s' % sql_map.url

def add_urls_to_storage(session, map_id, timestamp_url_list):

    for m in timestamp_url_list:  # (timestamp, url)
        try:
            min = m[0] - timedelta(seconds=10) # одна и таже карта могла добавиться с мммаленькой дельтой в миллисекунды
            max = m[0] + timedelta(seconds=10)
            found = session.query(Storage).filter(
                    and_(Storage.map_id == map_id,
                         and_(Storage.timestamp > min, Storage.timestamp < max))).all()
            if not len(found):
                path = file_storage.download(m[1], map_id, m[0])

                new_file = Storage(url=m[1], path=path, timestamp=m[0],
                          download_time=datetime.utcnow(),
                          map_id=map_id)
                session.add(new_file)
                session.commit()
        except Exception, err:
            log.error(err)


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

def get_region_by_location(latitude, longitude):

    with DBSession() as session:
        coordinates = [(o.latitude, o.longitude, o.radius, haversine(longitude, latitude, o.longitude, o.latitude), o.region_id) for o in session.query(Map).all()]
        coordinates = [c for c in coordinates if c[2] > c[3]]  # радиус карты > расстояние до клиента
        if not coordinates:
            return None

        coordinates = sorted(coordinates, key=lambda c: c[3])

        log.info("client coordinates: %f,%f" % (latitude, longitude))
        for c in coordinates[:3]:
            log.info("maps coordinates: %f,%f %d, distanse = %d km" % (c[0], c[1], c[2], int(c[3])))
        return coordinates[0][4]  # region_id

def get_map(map_id, timestamp):

    if not timestamp:
        return None, u'карта отсутствует'

    with DBSession() as session:
        sql_map = session.query(Map).get(map_id)

        if not sql_map.last_update or (datetime.utcnow() - sql_map.last_update).total_seconds() > sql_map.update_delay / 2: # Данные устарели
            timestamp_url_list = current_map_urls(sql_map)

            if not timestamp_url_list:
                log.error('ни одной карты на странице!')
                return None, u'нет карт на странице'
            else:
                add_urls_to_storage(session, sql_map.id, timestamp_url_list)

            sql_map.last_update = datetime.utcnow()  # только после добавления. вдруг exception
            session.commit()

        try:
            sql_file = found_next_map_in_storage(session, sql_map, timestamp)
            if not sql_file:
                raise NoResultFound()

            return sql_file.path, get_map_info(session, sql_map, sql_file.timestamp)

        except NoResultFound:
            # нет будущих карт. вернем предыдущую, если она моложе времени предыдущего обновления
            try:
                sql_file = found_next_map_in_storage(session, sql_map, timestamp-timedelta(seconds=sql_map.update_delay))
                if not sql_file:
                    raise NoResultFound()

                return sql_file.path, get_map_info(session, sql_map, sql_file.timestamp)

            except NoResultFound:
                return None, u'карта отсутствует'


def get_map_info(session, sql_map, timestamp):
    sql_map_type = session.query(MapType).get(sql_map.map_type_id)
    sql_region = session.query(Region).get(sql_map.region_id)
    return u'%s:%s\n%s\nЛегенда: /legend' % (sql_region.name_rus, sql_map_type.name_rus,
                                          timestamp.strftime('%d.%m.%Y %H:%M UTC'))


def get_previous_timestamp_by_path(path):
    with DBSession() as session:
        try:
            storage_file = session.query(Storage).filter(Storage.path == path).one()
        except MultipleResultsFound:
            log.error("multiple objects in Storage with path=%s" % path)
            storage_file = session.query(Storage).filter(Storage.path == path).all()
            for f in storage_file:
                log.info(str(f))
            storage_file = storage_file[0]

        sql_map = session.query(Map).get(storage_file.map_id)
        sql_file = found_previous_map_in_storage(session, sql_map, storage_file.timestamp-timedelta(seconds=1))
        return sql_file.timestamp if sql_file else None


def get_next_timestamp_by_path(path):
    with DBSession() as session:
        try:
            storage_file = session.query(Storage).filter(Storage.path == path).one()
        except MultipleResultsFound:
            log.error("multiple objects in Storage with path=%s" % path)
            storage_file = session.query(Storage).filter(Storage.path == path).all()
            for f in storage_file:
                log.info(str(f))
            storage_file = storage_file[0]

        sql_map = session.query(Map).get(storage_file.map_id)
        sql_file = found_next_map_in_storage(session, sql_map, storage_file.timestamp+timedelta(seconds=1))
        return sql_file.timestamp if sql_file else None
