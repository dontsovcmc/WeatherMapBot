# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from datetime import datetime

from maps.weather_map import WeatherMap


class PictureMap(WeatherMap):
    def __init__(self, name, bot_path, info, url, update_delay, region, mtype, legend_id):
        WeatherMap.__init__(self, name, bot_path, info, url, update_delay, region, mtype, legend_id)

    def get_current_map_urls(self):
        #на каждый запрос будет возвращена карта (
        return [(datetime.now(), self.url)]
