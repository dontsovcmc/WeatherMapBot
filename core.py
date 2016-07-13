# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from telegram import KeyboardButton

downloaded_files = {}

class WeatherMap(object):
    def __init__(self, name, id):
        """
        name = имя для кнопок меню
        id = информация о карте
        """
        self.name = name
        self.id = id

    def update(self):
        pass

    def now(self):
        pass


class WeatherSite():
    def __init__(self, name, maps):
        """
        name = имя для кнопок меню
        maps = список WeatherMap
        """
        self.name = name
        self.maps = maps

    def get(self, name):
        """
        Поиск карты по имени
        """
        found = [m for m in self.maps if m.name == name]
        if found:
            return found[0]

    def keyboard_layout(self):
        """
        Список списков для отображения меню по строкам
        """
        def add_kb(maps):
            return [KeyboardButton(m.name) for m in maps]
        return [add_kb(self.maps[x:x+3]) for x in xrange(0, len(self.maps), 3)]


class WeatherSites():
    def __init__(self, sites):
        """
        sites = список WeatherSite
        """
        self.sites = sites

    def get(self, name):
        """
        Поиск сайта по имени
        """
        found = [s for s in self.sites if s.name == name]
        if found:
            return found[0]

    def keyboard_layout(self):
        """
        Список списков для отображения меню по строкам
        """
        def add_kb(maps):
            return [KeyboardButton(m.name) for m in maps]
        return [add_kb(self.sites[x:x+3]) for x in xrange(0, len(self.sites), 3)]