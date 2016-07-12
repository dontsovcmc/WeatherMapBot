# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import httplib
import bs4
from datetime import datetime

EUROPE = 'eur'
SIBERIA = 'sib'
FAR_EAST = 'feru'

CLOUDS = 'clou'
OSADKI = 'prc'
WIND = 'wind'
TEMPERATURE = 'temp'


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


class Map(GisMeteoPage):
    def __init__(self, name, url):
        GisMeteoPage.__init__(self, '/map/' + url + '/')
        self.name = name.decode('utf-8')

    def now(self):
        return self.name + '\n' + GisMeteoPage.now(self)