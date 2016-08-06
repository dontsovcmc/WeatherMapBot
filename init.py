# -*- coding: utf-8 -*-
__author__ = 'dontsov'

import os
from sqlalchemy.orm.exc import NoResultFound

from db import DBSession, engine, Map, Site, Legend, Base, MapType, Continent, Region, ParseType
from logger import log
from maps import weather_maps
from maps import elegends, emaptype, eregion, econtinent, eparsetype

def init():

    def get_sql_site(session, weather_map):
        url = weather_map.url.split('//')[1].split('/')[0]
        try:
            sql_site = session.query(Site).filter(Site.url==url).one()
        except NoResultFound:
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


    def add_parse_type(session, id):
        pt = session.query(ParseType).get(id)
        if not pt:
            pt = ParseType()
            session.add(pt)


    if not os.path.isfile('weather_map.db'):
        Base.metadata.create_all(engine)


    with DBSession() as session:

        add_parse_type(session, eparsetype.GISMETEO_MAP)
        add_parse_type(session, eparsetype.PICTURE_MAP)
        add_parse_type(session, eparsetype.LINK_MAP)

        add_map_type(session, emaptype.radar, u'Радар')
        add_map_type(session, emaptype.temp_actions, u'Температура и явления погоды')
        add_map_type(session, emaptype.airtemperature, u'Температура воздуха')
        add_map_type(session, emaptype.clouds, u'Облачность и фронты')
        add_map_type(session, emaptype.osadki, u'Осадки')
        add_map_type(session, emaptype.wind, u'Приземный ветер')
        add_map_type(session, emaptype.hurricane, u'Тайфуны,ураганы')


        add_continent(session, econtinent.eurasia_russia, u'Евразия:Россия')
        add_continent(session, econtinent.eurasia_europe, u'Евразия:Европа')
        add_continent(session, econtinent.eurasia_asia, u'Евразия:Азия')
        add_continent(session, econtinent.north_america, u'Северная Америка')
        add_continent(session, econtinent.south_america, u'Южная Америка')
        add_continent(session, econtinent.africa, u'Африка')
        add_continent(session, econtinent.antarctic, u'Антарктика')

        session.commit()

        add_region(session, eregion.europe, econtinent.eurasia_europe, u'Европа')
        add_region(session, eregion.mediterranean, econtinent.eurasia_europe, u'Средиземноморье')
        add_region(session, eregion.baltic, econtinent.eurasia_europe, u'Прибалтика')
        add_region(session, eregion.ukraine, econtinent.eurasia_europe, u'Украина')
        add_region(session, eregion.belarus, econtinent.eurasia_europe, u'Беларусь')
        add_region(session, eregion.moldova, econtinent.eurasia_europe, u'Молдова')

        add_region(session, eregion.moscow_region, econtinent.eurasia_russia, u'Московская область')
        add_region(session, eregion.spb, econtinent.eurasia_russia, u'Санкт-Петербург')
        add_region(session, eregion.black_sea, econtinent.eurasia_russia, u'Черноморское побережье')
        add_region(session, eregion.russia_central, econtinent.eurasia_russia, u'Центральная Россия')
        add_region(session, eregion.ural, econtinent.eurasia_russia, u'Урал')
        add_region(session, eregion.siberia, econtinent.eurasia_russia, u'Сибирь')
        add_region(session, eregion.north_siberia, econtinent.eurasia_russia, u'Север Сибири')
        add_region(session, eregion.south_siberia, econtinent.eurasia_russia, u'Юг Сибири')
        add_region(session, eregion.far_east, econtinent.eurasia_russia, u'Дальний Восток')

        add_region(session, eregion.antarctic, econtinent.antarctic, u'Антарктика')
        add_region(session, eregion.north_america, econtinent.north_america, u'Северная Америка')
        add_region(session, eregion.south_america, econtinent.south_america, u'Южная Америка')
        add_region(session, eregion.south_east_asia, econtinent.eurasia_asia, u'Юго-Восточная Азия')
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
                except NoResultFound:
                    log.warning("Not found map with URL=%s, create it" % m.url)
                    new_map = Map(bot_path=m.bot_path)
                    session.add(new_map)

                sql_parse_type = session.query(ParseType).get(m.parse_type)
                sql_site = get_sql_site(session, m)
                sql_map_type = session.query(MapType).get(m.map_type_id)
                sql_region = session.query(Region).get(m.region_id)
                sql_legend = session.query(Legend).get(m.legend_id)

                new_map.bot_path = m.bot_path
                new_map.info = m.info
                new_map.url = m.url
                new_map.update_delay = m.update_delay

                new_map.latitude = m.latitude
                new_map.longitude = m.longitude
                new_map.radius = m.radius

                new_map.parse_type_id = sql_parse_type.id
                new_map.region_id = sql_region.id
                new_map.map_type_id = sql_map_type.id
                new_map.legend_id = sql_legend.id
                new_map.site_id = sql_site.id

            except Exception, err:
                log.error("Init DB error %s" % str(err))
                log.error(err)

