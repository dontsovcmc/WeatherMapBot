# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from core import WeatherMap

class PictureMap(WeatherMap):
    def __init__(self, name, id):
        WeatherMap.__init__(self, name, id)

    def now(self):
        return self.name + '\n' + self.id

