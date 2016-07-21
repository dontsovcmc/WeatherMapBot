# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from datetime import datetime

import bs4
from maps.weather_map import WeatherMap
from network import Downloader


# return f[0].strftime('%d.%m.%Y %H:%M') + '\n' + f[1]


class GisMeteoMap(WeatherMap):
    def __init__(self, name, info, url, update_delay, region, mtype, legend_id):
        '''

        :param name:
        :param info:
        :param url: bot_path
        :param update_delay:
        :param region:
        :param mtype:
        :param legend_id:
        :return:
        '''
        WeatherMap.__init__(self, name, url, info, 'https://www.gismeteo.ru/maps/' + url + '/', update_delay, region, mtype, legend_id)

    def get_current_map_urls(self):
        """
        [(timestamp, url)]
        :return:
        """
        with Downloader() as d:
            data = d.getresponse(self.url)
            soup = bs4.BeautifulSoup(data, "html.parser")

        frames = []
        tab_i = 0
        try:
            while True:
                imgs = soup.select('.tab%s > img' % tab_i)
                if not imgs:
                    return
                for i in imgs:
                    date_object = datetime.strptime(i.attrs['alt'], '%d.%m.%Y %H:%M')
                    frame = date_object, 'https:' + i.attrs['title']
                    frames.append(frame)
                tab_i += 1
        except Exception, err:
            pass

        return frames


def test():
    pass