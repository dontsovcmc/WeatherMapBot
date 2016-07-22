# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from datetime import datetime
from storage import file_storage

class WeatherMap(object):
    def __init__(self, map_type, name, bot_path, info, url, update_delay, region, mtype, legend):
        '''
        :param name: имя для кнопок меню
        :param id: информация о карте
        :return:
        '''
        self.map_type = map_type
        self.name = name
        self.bot_path = bot_path
        self.info = info
        self.url = url
        self.update_delay = update_delay # время обновления карт
        self.region = region
        self.mtype = mtype
        self.legend = legend
