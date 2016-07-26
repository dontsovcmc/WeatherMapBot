# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from maps.weather_map import WeatherMap

GISMETEO_MAP, PICTURE_MAP, LINK_MAP = range(3)

class elegends():
    gismeteo_ru_clouds = 1
    gismeteo_ru_airtemperature = 2
    gismeteo_ru_temp_actions = 3
    gismeteo_ru_wind = 4
    gismeteo_ru_hurricane = 5
    gismeteo_ru_radar = 6
    meteoinfo_by_radar = 7
    gismeteo_ru_osadki = 8

class emaptype():
    clouds = 1
    airtemperature = 2
    temp_actions = 3
    wind = 4
    hurricane = 5
    radar = 6
    osadki = 7

class econtinent():
    africa = 1
    eurasia_europe = 2
    eurasia_russia = 3
    eurasia_asia = 4
    north_america = 5
    south_america = 6
    antarctic = 7


class eregion():
    antarctic = 1
    baltic = 2
    belarus = 3
    black_sea = 4
    europe = 5
    far_east = 6
    mediterranean = 7
    moldova = 8
    moscow_region = 9
    north_america = 10
    north_siberia = 11
    russia_central = 12
    siberia = 13
    south_america = 14
    south_east_asia = 15
    south_siberia = 16
    ukraine = 17
    ural = 18
    spb = 19
    africa = 20


weather_maps = [
    WeatherMap(GISMETEO_MAP, '549', '', 'https://www.gismeteo.ru/map/549/', 360*60,emaptype.osadki, eregion.south_america, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '555', '', 'https://www.gismeteo.ru/map/555/', 360*60,emaptype.osadki, eregion.south_east_asia, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '558', '', 'https://www.gismeteo.ru/map/558/', 360*60,emaptype.osadki, eregion.europe, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '569', '', 'https://www.gismeteo.ru/map/569/', 360*60,emaptype.osadki, eregion.moscow_region, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '572', '', 'https://www.gismeteo.ru/map/572/', 360*60,emaptype.osadki, eregion.russia_central, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '576', '', 'https://www.gismeteo.ru/map/576/', 360*60,emaptype.osadki, eregion.far_east, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '593', '', 'https://www.gismeteo.ru/map/593/', 360*60,emaptype.osadki, eregion.ural, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '595', '', 'https://www.gismeteo.ru/map/595/', 360*60,emaptype.osadki, eregion.black_sea, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '597', '', 'https://www.gismeteo.ru/map/597/', 360*60,emaptype.osadki, eregion.mediterranean, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '599', '', 'https://www.gismeteo.ru/map/599/', 360*60,emaptype.osadki, eregion.ukraine, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '608', '', 'https://www.gismeteo.ru/map/608/', 360*60,emaptype.osadki, eregion.south_siberia, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '614', '', 'https://www.gismeteo.ru/map/614/', 360*60,emaptype.osadki, eregion.belarus, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '617', '', 'https://www.gismeteo.ru/map/617/', 360*60,emaptype.osadki, eregion.africa, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '618', '', 'https://www.gismeteo.ru/map/618/', 360*60,emaptype.osadki, eregion.baltic, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '648', '', 'https://www.gismeteo.ru/map/648/', 360*60,emaptype.osadki, eregion.antarctic, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '652', '', 'https://www.gismeteo.ru/map/652/', 360*60,emaptype.osadki, eregion.siberia, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '660', '', 'https://www.gismeteo.ru/map/660/', 360*60,emaptype.osadki, eregion.north_siberia, elegends.gismeteo_ru_osadki),
    WeatherMap(GISMETEO_MAP, '561', '', 'https://www.gismeteo.ru/map/561/', 360*60,emaptype.clouds, eregion.europe, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '562', '', 'https://www.gismeteo.ru/map/562/', 360*60,emaptype.clouds, eregion.siberia, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '563', '', 'https://www.gismeteo.ru/map/563/', 360*60,emaptype.clouds, eregion.far_east, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '568', '', 'https://www.gismeteo.ru/map/568/', 360*60,emaptype.clouds, eregion.russia_central, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '573', '', 'https://www.gismeteo.ru/map/573/', 360*60,emaptype.clouds, eregion.north_siberia, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '574', '', 'https://www.gismeteo.ru/map/574/', 360*60,emaptype.clouds, eregion.baltic, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '581', '', 'https://www.gismeteo.ru/map/581/', 360*60,emaptype.clouds, eregion.black_sea, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '582', '', 'https://www.gismeteo.ru/map/582/', 360*60,emaptype.clouds, eregion.ural, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '592', '', 'https://www.gismeteo.ru/map/592/', 360*60,emaptype.clouds, eregion.ukraine, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '598', '', 'https://www.gismeteo.ru/map/598/', 360*60,emaptype.clouds, eregion.mediterranean, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '607', '', 'https://www.gismeteo.ru/map/607/', 360*60,emaptype.clouds, eregion.south_siberia, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '613', '', 'https://www.gismeteo.ru/map/613/', 360*60,emaptype.clouds, eregion.belarus, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '662', '', 'https://www.gismeteo.ru/map/662/', 360*60,emaptype.clouds, eregion.south_east_asia, elegends.gismeteo_ru_clouds),
    WeatherMap(GISMETEO_MAP, '557', '', 'https://www.gismeteo.ru/map/557/', 360*60,emaptype.airtemperature, eregion.europe, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '559', '', 'https://www.gismeteo.ru/map/559/', 360*60,emaptype.airtemperature, eregion.siberia, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '560', '', 'https://www.gismeteo.ru/map/560/', 360*60,emaptype.airtemperature, eregion.far_east, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '570', '', 'https://www.gismeteo.ru/map/570/', 360*60,emaptype.airtemperature, eregion.russia_central, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '575', '', 'https://www.gismeteo.ru/map/575/', 360*60,emaptype.airtemperature, eregion.north_siberia, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '583', '', 'https://www.gismeteo.ru/map/583/', 360*60,emaptype.airtemperature, eregion.ural, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '586', '', 'https://www.gismeteo.ru/map/586/', 360*60,emaptype.airtemperature, eregion.baltic, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '591', '', 'https://www.gismeteo.ru/map/591/', 360*60,emaptype.airtemperature, eregion.ukraine, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '596', '', 'https://www.gismeteo.ru/map/596/', 360*60,emaptype.airtemperature, eregion.black_sea, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '610', '', 'https://www.gismeteo.ru/map/610/', 360*60,emaptype.airtemperature, eregion.south_siberia, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '611', '', 'https://www.gismeteo.ru/map/611/', 360*60,emaptype.airtemperature, eregion.moscow_region, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '612', '', 'https://www.gismeteo.ru/map/612/', 360*60,emaptype.airtemperature, eregion.belarus, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '615', '', 'https://www.gismeteo.ru/map/615/', 360*60,emaptype.airtemperature, eregion.mediterranean, elegends.gismeteo_ru_airtemperature),
    WeatherMap(GISMETEO_MAP, '542', '', 'https://www.gismeteo.ru/map/542/', 360*60,emaptype.temp_actions, eregion.far_east, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '554', '', 'https://www.gismeteo.ru/map/554/', 360*60,emaptype.temp_actions, eregion.siberia, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '594', '', 'https://www.gismeteo.ru/map/594/', 360*60,emaptype.temp_actions, eregion.ukraine, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '600', '', 'https://www.gismeteo.ru/map/600/', 360*60,emaptype.temp_actions, eregion.mediterranean, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '620', '', 'https://www.gismeteo.ru/map/620/', 360*60,emaptype.temp_actions, eregion.south_siberia, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '622', '', 'https://www.gismeteo.ru/map/622/', 360*60,emaptype.temp_actions, eregion.russia_central, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '623', '', 'https://www.gismeteo.ru/map/623/', 360*60,emaptype.temp_actions, eregion.baltic, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '624', '', 'https://www.gismeteo.ru/map/624/', 360*60,emaptype.temp_actions, eregion.moscow_region, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '625', '', 'https://www.gismeteo.ru/map/625/', 360*60,emaptype.temp_actions, eregion.europe, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '649', '', 'https://www.gismeteo.ru/map/649/', 360*60,emaptype.temp_actions, eregion.moldova, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '659', '', 'https://www.gismeteo.ru/map/659/', 360*60,emaptype.temp_actions, eregion.ural, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '661', '', 'https://www.gismeteo.ru/map/661/', 360*60,emaptype.temp_actions, eregion.north_siberia, elegends.gismeteo_ru_temp_actions),
    WeatherMap(GISMETEO_MAP, '601', '', 'https://www.gismeteo.ru/map/601/', 360*60,emaptype.wind, eregion.black_sea, elegends.gismeteo_ru_wind),
    WeatherMap(GISMETEO_MAP, '602', '', 'https://www.gismeteo.ru/map/602/', 360*60,emaptype.wind, eregion.baltic, elegends.gismeteo_ru_wind),
    WeatherMap(GISMETEO_MAP, '603', '', 'https://www.gismeteo.ru/map/603/', 360*60,emaptype.wind, eregion.far_east, elegends.gismeteo_ru_wind),
    WeatherMap(GISMETEO_MAP, '609', '', 'https://www.gismeteo.ru/map/609/', 360*60,emaptype.wind, eregion.south_siberia, elegends.gismeteo_ru_wind),
    WeatherMap(GISMETEO_MAP, '616', '', 'https://www.gismeteo.ru/map/616/', 360*60, emaptype.hurricane, eregion.far_east, elegends.gismeteo_ru_hurricane),
    WeatherMap(GISMETEO_MAP, '630', '', 'https://www.gismeteo.ru/map/630/', 360*60, emaptype.hurricane, eregion.north_america, elegends.gismeteo_ru_hurricane),
    WeatherMap(GISMETEO_MAP, '646', '', 'https://www.gismeteo.ru/map/646/', 10*60, emaptype.radar, eregion.black_sea, elegends.gismeteo_ru_radar),
    WeatherMap(GISMETEO_MAP, '647', '', 'https://www.gismeteo.ru/map/647/', 10*60, emaptype.radar, eregion.moscow_region, elegends.gismeteo_ru_radar),
    WeatherMap(GISMETEO_MAP, '657', '', 'https://www.gismeteo.ru/map/657/', 10*60, emaptype.radar, eregion.belarus, elegends.gismeteo_ru_radar),
    WeatherMap(GISMETEO_MAP, '658', '', 'https://www.gismeteo.ru/map/658/', 10*60, emaptype.radar, eregion.baltic, elegends.gismeteo_ru_radar),

    WeatherMap(PICTURE_MAP, 'spb_radar', '', 'http://meteoinfo.by/radar/RUSP/RUSP_latest.png/', 360*60, emaptype.radar, eregion.spb, elegends.meteoinfo_by_radar),
]

#PictureMap(u'СПБ: Радар (анимир)', 'http://meteoinfo.by/radar/RUSP/radar-map.gif')]

