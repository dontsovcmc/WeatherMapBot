# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from datetime import datetime
from storage import file_storage

class WeatherMap(object):
    def __init__(self, parse_type, bot_path, info, url, update_delay, map_type_id, region_id, legend_id):
        '''
        :param name: имя для кнопок меню
        :param id: информация о карте
        :return:
        '''
        self.parse_type = parse_type
        self.bot_path = bot_path
        self.info = info
        self.url = url
        self.update_delay = update_delay # время обновления карт

        self.region_id = region_id
        self.map_type_id = map_type_id
        self.legend_id = legend_id
