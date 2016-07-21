# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from core import WeatherSite, WeatherSites, WeatherMap
from GisMeteoParser import GisMeteoMap
from PictureMap import PictureMap


change_site = WeatherMap(u'Выбор сайта', '')

maps = [
    GisMeteoMap(u'МО: Осадки', '', '569', 0, 'moscow_region', 'osadki', None),
    GisMeteoMap(u'МО: Радар', '', '', '647', 0, 'moscow_region', 'radar', None),
    GisMeteoMap(u'Сочи: Радар', '', '646', 0, 'sochi', 'radar', None),
    GisMeteoMap(u'Ц.Россия: Осадки', '', '572', 0, 'russia', 'osadki', None),
    GisMeteoMap(u'Ц.Россия: Облачность', '', '568', 0, 'russia', 'clouds', None),
    GisMeteoMap(u'Ц.Россия: T возд', '', '570', 0, 'russia', 'temperature', None),


    PictureMap(u'СПБ: Радар', '', 'http://meteoinfo.by/radar/RUSP/RUSP_latest.png', 600, 'spb', 'radar', None),
]
#PictureMap(u'СПБ: Радар (анимир)', 'http://meteoinfo.by/radar/RUSP/radar-map.gif')]

