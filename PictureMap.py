# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from core import WeatherMap
from storage import file_storage
from datetime import datetime
from logger import log

class PictureMap(WeatherMap):
    def __init__(self, name, info, url, update_delay, region, mtype, legend_id):
        WeatherMap.__init__(self, name, info, url, update_delay, region, mtype, legend_id)

    def get_current_map_urls(self):
        #на каждый запрос будет возвращена карта (
        return [(datetime.now(), self.url)]
