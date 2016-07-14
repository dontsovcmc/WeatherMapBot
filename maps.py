# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from core import WeatherSite, WeatherSites, WeatherMap
from GisMeteoParser import GisMeteoMap
from PictureMap import PictureMap


change_site = WeatherMap(u'Выбор сайта', '')


weather_sites = WeatherSites([
    WeatherSite('gismeteo_ru', 'gismeteo_ru',
                [GisMeteoMap(u'МО: Осадки', '569'), GisMeteoMap(u'МО: Радар', '647'), GisMeteoMap(u'Сочи: Радар', '646'),
                 GisMeteoMap(u'Ц.Россия: Осадки', '572'), GisMeteoMap(u'Ц.Россия: Облачность', '568'), GisMeteoMap(u'Ц.Россия: T возд', '570'),
                 change_site]),
    WeatherSite('meteoinfo_by', 'meteoinfo_by',
                [PictureMap(u'СПБ: Радар', 'http://meteoinfo.by/radar/RUSP/RUSP_latest.png'),
                 PictureMap(u'СПБ: Радар (анимир)', 'http://meteoinfo.by/radar/RUSP/radar-map.gif')])])

