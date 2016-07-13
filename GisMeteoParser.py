# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import httplib
import bs4
from datetime import datetime

from core import WeatherMap

from network import Downloader

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
                    frame = date_object, i.attrs['title'][2:]
                    self.frames.append(frame)
                tab_i += 1

        except Exception, err:
            pass

    def all(self):
        return '\n'.join(self.frames)

    def now(self):
        n = datetime.now()
        for f in self.frames:
            if f[0] > n:
                return f[0].strftime('%d.%m.%Y %H:%M') + '\n' + f[1]
        return ''


class GisMeteoMap(WeatherMap):
    def __init__(self, name, id):
        WeatherMap.__init__(self, name, id)
        self.page = GisMeteoPage('/map/' + id + '/')

    def now(self):

        def latest():
            n = datetime.now()
            for f in self.page.frames:
                if f[0] > n:
                    return f[0].strftime('%d.%m.%Y %H:%M'), f[1]
            return n.strftime('%d.%m.%Y %H:%M'), ''

        t, url = latest()

        path = FileStorage.get(url)

        return t, path

    def update(self):
        return self.page.update()


def test():
    pass