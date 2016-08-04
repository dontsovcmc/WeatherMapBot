# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from datetime import datetime
from storage import file_storage

class WeatherMap(object):
    def __init__(self, parse_type, bot_path, info, url, update_delay, coordinate, map_type_id, region_id, legend_id):
        """

        :param parse_type: Тип парсера, который обрабатывает страницу url
        :param bot_path: -
        :param info: -
        :param url: интернет страница с картой
        :param update_delay: время обновления карты, сек
        :param coordinate: (latitude, longitude, radius)
        :param map_type_id: тип карты
        :param region_id: тип региона
        :param legend_id: тип легенды
        :return:
        """
        self.parse_type = parse_type
        self.bot_path = bot_path
        self.info = info
        self.url = url
        self.update_delay = update_delay # время обновления карт

        self.latitude = coordinate[0]
        self.longitude = coordinate[1]
        self.radius = coordinate[2]

        self.region_id = region_id
        self.map_type_id = map_type_id
        self.legend_id = legend_id
