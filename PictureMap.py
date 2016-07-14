# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from core import WeatherMap
from storage import file_storage
from datetime import datetime
from logger import log

class PictureMap(WeatherMap):
    def __init__(self, name, id):
        WeatherMap.__init__(self, name, id)
        self.update_delay_sec = 300

    def get_map_by_time(self, timestamp):
        self.last_request = datetime.now()

        if self.update_needed():
            self.update()

        t = self.last_update

        path = file_storage.get(self.id)
        return t, path

    def update(self):
        self.last_update = datetime.now()
        log.info("PictureMap: update")
        path = file_storage.get(self.id, force=True)