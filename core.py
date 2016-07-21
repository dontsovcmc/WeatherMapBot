# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from datetime import datetime
from storage import file_storage
from db import add_map_to_storage, map_id

class WeatherMap(object):
    def __init__(self, name, info, url, update_delay, region, mtype, legend_id):
        '''
        :param name: имя для кнопок меню
        :param id: информация о карте
        :return:
        '''
        self.name = name
        self.info = info
        self.url = url
        self.update_delay = update_delay # время обновления карт
        self.region = region
        self.mtype = mtype
        self.legend_id = legend_id

    def get_current_map_urls(self):
        pass

    def update(self):
        timestamp_urls = self.get_current_map_urls()

        for m in timestamp_urls: # (timestamp, url)
            path = file_storage.get(m[1], force=False)

            add_map_to_storage(map_id(self.name),
                               m[1],
                               path,
                               m[0],
                               datetime.utcnow())


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
