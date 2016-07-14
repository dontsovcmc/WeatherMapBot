# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import httplib
import bs4
from datetime import datetime, timedelta

from core import WeatherMap
from storage import file_storage

from network import Downloader
from logger import log

class Connection(object):
    def __init__(self, url):
        self.root_url = 'www.gismeteo.ru'
        self.url = url

    def soup(self):
        conn = httplib.HTTPSConnection(self.root_url)
        conn.request('GET', self.url)
        r1 = conn.getresponse()
        soup = bs4.BeautifulSoup(r1.read(), "html.parser")
        conn.close()
        return soup


class GisMeteoPage(Connection):

    def __init__(self, url):
        Connection.__init__(self, url)
        self.frames = []

    def update(self):
        soup = self.soup()
        tab_i = 0
        try:
            while True:
                imgs = soup.select('.tab%s > img' % tab_i)
                if not imgs:
                    return
                for i in imgs:
                    date_object = datetime.strptime(i.attrs['alt'], '%d.%m.%Y %H:%M')
                    frame = date_object, 'https:' + i.attrs['title']
                    self.frames.append(frame)
                tab_i += 1

        except Exception, err:
            pass

    def all(self):
        return '\n'.join(self.frames)

    def now(self):
        n = datetime.now()
        self.last_request = n

        for f in self.frames:
            if f[0] > n:
                return f[0].strftime('%d.%m.%Y %H:%M') + '\n' + f[1]
        return ''


class GisMeteoMap(WeatherMap):
    def __init__(self, name, id):
        WeatherMap.__init__(self, name, id)
        self.page = GisMeteoPage('/map/' + id + '/')

    def get_map_by_time(self, timestamp):
        self.last_request = datetime.now()

        def latest():
            for f in self.page.frames:
                if f[0] > timestamp:
                    return f[0], f[1]
            return timestamp, ''

        if self.update_needed():
            log.info("GisMeteoMap: update")
            self.page.update()
            self.calculate_update_delay()
            self.last_update = latest()[0] - timedelta(seconds=self.update_delay_sec)

        t, url = latest()
        log.info('GisMeteoMap: map: %s' % url)
        path = file_storage.get(url)
        log.info('GisMeteoMap: path: %s' % path)
        return t, path

    def calculate_update_delay(self):
        if len(self.page.frames) > 1:
            self.update_delay_sec = (self.page.frames[1][0] - self.page.frames[0][0]).total_seconds()
            log.info("GisMeteoMap: %s update delay %s sec" % (self.name, str(self.update_delay_sec)))

def test():
    pass