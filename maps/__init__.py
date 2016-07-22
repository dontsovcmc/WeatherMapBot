# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from maps.weather_map import WeatherMap

GISMETEO_MAP, PICTURE_MAP, LINK_MAP = range(3)

weather_maps = [
    WeatherMap(GISMETEO_MAP, u'МО: Осадки', '569', '', 'https://www.gismeteo.ru/maps/569/', 0, 'moscow_region', 'osadki', None),
    WeatherMap(GISMETEO_MAP, u'МО: Радар', '647', '', 'https://www.gismeteo.ru/maps/647/', 0, 'moscow_region', 'radar', None),
    WeatherMap(GISMETEO_MAP, u'Сочи: Радар', '646', '', 'https://www.gismeteo.ru/maps/646/', 0, 'sochi', 'radar', None),
    WeatherMap(GISMETEO_MAP, u'Ц.Россия: Осадки', '572','', 'https://www.gismeteo.ru/maps/572/', 0, 'russia', 'osadki', None),
    WeatherMap(GISMETEO_MAP, u'Ц.Россия: Облачность', '568', '', 'https://www.gismeteo.ru/maps/568/', 0, 'russia', 'clouds', None),
    WeatherMap(GISMETEO_MAP, u'Ц.Россия: T возд','570', '', 'https://www.gismeteo.ru/maps/570/', 0, 'russia', 'temperature', None),

    WeatherMap(PICTURE_MAP, u'СПБ: Радар', 'spb_radar', '', 'http://meteoinfo.by/radar/RUSP/RUSP_latest.png', 600, 'spb', 'radar', None),
]

#PictureMap(u'СПБ: Радар (анимир)', 'http://meteoinfo.by/radar/RUSP/radar-map.gif')]

