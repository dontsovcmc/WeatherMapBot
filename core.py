# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import os
import bs4

from network import Downloader
from db import DBSession, engine, Map, Site, Storage, Legend, Base, MapType, Continent, Region
from maps import weather_maps
from maps import GISMETEO_MAP, PICTURE_MAP, LINK_MAP
from logger import log
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_
from datetime import datetime, timedelta
from storage import file_storage
from maps import elegends, emaptype, eregion, econtinent

PREVIOUS_MAP = u'<<'
NEXT_MAP = u'>>'
CHANGE_CONT = u'Выбор континета'
CHANGE_REGION = u'Выбор региона'
CHANGE_MAP = u'Выбор типа карты'
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

    def add_map_type(session, id, name_rus):
        new_map = session.query(MapType).get(id)
        if new_map:
            new_map.name_rus = name_rus
        else:
            new_map = MapType(name_rus=name_rus)
            session.add(new_map)


    def add_continent(session, id, name_rus):
        new_cont = session.query(Continent).get(id)
        if new_cont:
            new_cont.name_rus = name_rus
        else:
            new_cont = Continent(name_rus=name_rus)
            session.add(new_cont)


    def add_region(session, id, continent_id, name_rus):
        cont = session.query(Continent).get(continent_id)
        new_region = session.query(Region).get(id)
        if new_region:
            new_region.continent_id = cont.id
            new_region.name_rus = name_rus
        else:
            new_region = Region(name_rus=name_rus, continent_id=cont.id)
            session.add(new_region)

    def add_legend(session, id, info):
        legend = session.query(Legend).get(id)
        if legend:
            legend.info = info
        else:
            legend = Legend(info=info)
            session.add(legend)



    if not os.path.isfile('weather_map.db'):
        Base.metadata.create_all(engine)



    with DBSession() as session:
        add_map_type(session, emaptype.clouds, u'Облачность и фронты')
        add_map_type(session, emaptype.airtemperature, u'Температура воздуха')
        add_map_type(session, emaptype.temp_actions, u'Температура и явления погоды')
        add_map_type(session, emaptype.wind, u'Приземный ветер')
        add_map_type(session, emaptype.hurricane, u'Тайфуны,ураганы')
        add_map_type(session, emaptype.radar, u'Радар')
        add_map_type(session, emaptype.osadki, u'Осадки')


        add_continent(session, econtinent.africa, u'Африка')
        add_continent(session, econtinent.eurasia_europe, u'Евразия:Европа')
        add_continent(session, econtinent.eurasia_russia, u'Евразия:Россия')
        add_continent(session, econtinent.eurasia_asia, u'Евразия:Азия')
        add_continent(session, econtinent.north_america, u'Северная Америка')
        add_continent(session, econtinent.south_america, u'Южная Америка')
        add_continent(session, econtinent.antarctic, u'Антарктика')

        session.commit()

        add_region(session, eregion.antarctic, econtinent.antarctic, u'Антарктика')
        add_region(session, eregion.baltic, econtinent.eurasia_europe, u'Прибалтика')
        add_region(session, eregion.belarus, econtinent.eurasia_europe, u'Беларусь')
        add_region(session, eregion.black_sea, econtinent.eurasia_russia, u'Черноморское побережье')
        add_region(session, eregion.europe, econtinent.eurasia_europe, u'Европа')
        add_region(session, eregion.far_east, econtinent.eurasia_russia, u'Дальний Восток')
        add_region(session, eregion.mediterranean, econtinent.eurasia_europe, u'Средиземноморье')
        add_region(session, eregion.moldova, econtinent.eurasia_europe, u'Молдова')
        add_region(session, eregion.moscow_region, econtinent.eurasia_russia, u'Московская область')
        add_region(session, eregion.north_america, econtinent.north_america, u'Северная Америка')
        add_region(session, eregion.north_siberia, econtinent.eurasia_russia, u'Север Сибири')
        add_region(session, eregion.russia_central, econtinent.eurasia_russia, u'Центральная Россия')
        add_region(session, eregion.siberia, econtinent.eurasia_russia, u'Сибирь')
        add_region(session, eregion.south_america, econtinent.south_america, u'Южная Америка')
        add_region(session, eregion.south_east_asia, econtinent.eurasia_asia, u'Юго-Восточная Азия')
        add_region(session, eregion.south_siberia, econtinent.eurasia_russia, u'Юг Сибири')
        add_region(session, eregion.ukraine, econtinent.eurasia_europe, u'Украина')
        add_region(session, eregion.ural, econtinent.eurasia_russia, u'Урал')
        add_region(session, eregion.spb, econtinent.eurasia_russia, u'Санкт-Петербург')
        add_region(session, eregion.africa, econtinent.africa, u'Африка')

        add_legend(session, elegends.gismeteo_ru_clouds, '')
        add_legend(session, elegends.gismeteo_ru_airtemperature, '')
        add_legend(session, elegends.gismeteo_ru_temp_actions, '')
        add_legend(session, elegends.gismeteo_ru_wind, '')
        add_legend(session, elegends.gismeteo_ru_hurricane, '')
        add_legend(session, elegends.gismeteo_ru_radar, '')
        add_legend(session, elegends.meteoinfo_by_radar, '')
        add_legend(session, elegends.gismeteo_ru_osadki, '')

        session.commit()

        for m in weather_maps:
            try:
                try:
                    new_map = session.query(Map).filter(Map.url == m.url).one()
                except NoResultFound, err:
                    new_map = Map(parse_type=m.parse_type,
                                  bot_path=m.bot_path)
                    session.add(new_map)

                sql_site = get_sql_site(session, m)
                sql_map_type = session.query(MapType).get(m.map_type_id)
                sql_region = session.query(Region).get(m.region_id)
                sql_legend = session.query(Legend).get(m.legend_id)

                new_map.parse_type = m.parse_type
                new_map.bot_path = m.bot_path
                new_map.info = m.info
                new_map.url = m.url
                new_map.update_delay = m.update_delay

                new_map.region_id = sql_region.id
                new_map.map_type_id = sql_map_type.id
                new_map.legend_id = sql_legend.id
                new_map.site_id = sql_site.id

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


def region_keyboard_layout(continent_id, kb):
    maps = []
    with DBSession() as session:
        regions = session.query(Region).filter(Region.continent_id == continent_id).all()
        for r in regions:
            maps.append(r.name_rus)

    maps.append(CHANGE_CONT)

    def add_kb(maps):
        return [kb(m) for m in maps]
    return [add_kb(maps[x:x+3]) for x in xrange(0, len(maps), 3)]


def maps_keyboard_layout(region_id, kb):
    maps = []
    with DBSession() as session:
        sql_region = session.query(Region).get(region_id)
        for m in session.query(Map).filter(Map.region_id == region_id).all():
            sql_map_type = session.query(MapType).get(m.map_type_id)
            maps.append(sql_map_type.name_rus) # format_sql_map_name(sql_region, sql_map_type))


    def add_kb(maps):
        return [kb(m) for m in maps]

    mkbd = [add_kb(maps[x:x+3]) for x in xrange(0, len(maps), 3)]
    mkbd.append([kb(CHANGE_CONT), kb(CHANGE_REGION)])
    return mkbd


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
            return sql_file.path, get_map_info(session, sql_map, sql_file.timestamp)

        except NoResultFound:
            return None, u'карта отсутствует'


def current_map_urls(sql_map):
    """
    [(timestamp, url)]
    :return:
    """
    frames = []
    if sql_map.parse_type == GISMETEO_MAP:

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

    elif sql_map.parse_type == PICTURE_MAP:

        return [(datetime.now(), sql_map.url)]

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
