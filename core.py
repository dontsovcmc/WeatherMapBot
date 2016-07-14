# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from telegram import KeyboardButton, InlineKeyboardButton
from datetime import datetime

downloaded_files = {}

class WeatherMap(object):
    def __init__(self, name, id):
        '''
        :param name: имя для кнопок меню
        :param id: информация о карте
        :return:
        '''
        self.name = name
        self.id = id
        self.update_delay_sec = 0 # время обновления карт
        self.last_request = None
        self.last_update = None

    def update(self):
        pass

    def now(self):
        return self.get_map_by_time(datetime.now())

    def get_map_by_time(self, timestamp):
        pass

    def map_info(self, timestamp):
        '''
        Текст над картой в сообщении
        :param timestamp: время карты
        :return: текст
        '''
        return '%s\n%s' % (self.name, timestamp.strftime('%d.%m.%Y %H:%M'))

    def update_needed(self):
        if self.update_delay_sec and self.last_update:
            n = datetime.now()
            return (n - self.last_update).total_seconds() > self.update_delay_sec
        return True


class WeatherSite():
    def __init__(self, name, cb, maps):
        '''
        :param name: имя для кнопок меню
        :param maps: список WeatherMap
        :return:
        '''
        self.name = name
        self.maps = maps
        self.cb = cb

    def get(self, name):
        '''
        Поиск карты по имени
        :param name:
        :return:
        '''
        found = [m for m in self.maps if m.name == name]
        if found:
            return found[0]

    def keyboard_layout(self):
        '''
        :return: Список списков для отображения меню по строкам
        '''
        def add_kb(maps):
            return [KeyboardButton(m.name) for m in maps]
        return [add_kb(self.maps[x:x+3]) for x in xrange(0, len(self.maps), 3)]


class WeatherSites():
    def __init__(self, sites):
        '''
        :param sites: список WeatherSite
        :return:
        '''
        self.sites = sites

    def get(self, name):
        '''
        Поиск сайта по имени
        :param name:
        :return:
        '''
        found = [s for s in self.sites if s.name == name]
        if found:
            return found[0]

    def keyboard_layout(self):
        '''
        Список списков для отображения меню по строкам
        :return:
        '''
        def add_kb(sites):
            return [KeyboardButton(s.name, callback_data=s.cb) for s in sites]
        return [add_kb(self.sites[x:x+3]) for x in xrange(0, len(self.sites), 3)]