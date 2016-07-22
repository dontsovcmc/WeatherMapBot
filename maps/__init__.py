# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from maps.weather_map import WeatherMap

GISMETEO_MAP, PICTURE_MAP, LINK_MAP = range(3)

weather_maps = [
    WeatherMap(GISMETEO_MAP, u'МО: Осадки', '569', '', 'https://www.gismeteo.ru/map/569/', 360*60, 'moscow_region', 'osadki', None),
    WeatherMap(GISMETEO_MAP, u'МО: Радар', '647', '', 'https://www.gismeteo.ru/map/647/', 45*60, 'moscow_region', 'radar', None),
    WeatherMap(GISMETEO_MAP, u'Сочи: Радар', '646', '', 'https://www.gismeteo.ru/map/646/', 45*60, 'sochi', 'radar', None),
    WeatherMap(GISMETEO_MAP, u'Ц.Россия: Осадки', '572','', 'https://www.gismeteo.ru/map/572/', 360*60, 'russia', 'osadki', None),
    WeatherMap(GISMETEO_MAP, u'Ц.Россия: Облачность', '568', '', 'https://www.gismeteo.ru/map/568/', 360*60, 'russia', 'clouds', None),
    WeatherMap(GISMETEO_MAP, u'Ц.Россия: T возд','570', '', 'https://www.gismeteo.ru/map/570/', 360*60, 'russia', 'temperature', None),

    WeatherMap(PICTURE_MAP, u'СПБ: Радар', 'spb_radar', '', 'http://meteoinfo.by/radar/RUSP/RUSP_latest.png', 10*60, 'spb', 'radar', None),
]

#PictureMap(u'СПБ: Радар (анимир)', 'http://meteoinfo.by/radar/RUSP/radar-map.gif')]

