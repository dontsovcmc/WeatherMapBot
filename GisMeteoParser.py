# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import httplib
import bs4
import os
import tempfile
from datetime import datetime
from PIL import Image

EUROPE = 'eur'
SIBERIA = 'sib'
FAR_EAST = 'feru'

CLOUDS = 'clou'
OSADKI = 'prc'
WIND = 'wind'
TEMPERATURE = 'temp'


class Downloader(object):

    def __init__(self):
        self.root_url = None
        self.conn = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k, v in self.conn.iteritems():
            v.close()

    def download_file(self, path, full_url):
        full_url = full_url.lstrip('/')
        server = full_url.split('/')[0]
        fname = full_url.split('/')[-1].split('?')[0]
        url = full_url[full_url.find('/'):]

        if not server in self.conn:
            self.conn[server] = httplib.HTTPSConnection(server)

        conn = self.conn[server]

        conn.request('GET', url)
        r1 = conn.getresponse()
        data = r1.read()
        filepath = os.path.join(path, fname)
        with open(filepath, 'wb') as f:
            f.write(data)
        return filepath


class Connection(object):

    def __init__(self, root, url):
        self.root_url = root
        self.url = url

    def soup(self):
        conn = httplib.HTTPSConnection(self.root_url)
        conn.request('GET', self.url)
        r1 = conn.getresponse()
        soup = bs4.BeautifulSoup(r1.read(), "html.parser")
        conn.close()
        return soup


# =============================================================================

class BetaGisMeteoPage(Connection):

    def __init__(self, url):
        Connection.__init__(self, 'beta.gismeteo.ru', url)
        self.frames = []

    def update(self):
        soup = self.soup()

        try:
            imgs1 = soup.select('.layout-1 img')
            imgs2 = soup.select('.layout-2 img')
            background_img1 = soup.select('.layout-0')[0].attrs['data-src']  #underground
            background_img2 = soup.select('.layout-3')[0].attrs['data-src']  #georgraphy
            dates = soup.select('.right_col > ul > li')

            for idx, val in enumerate(imgs1):
                stamp = dates[idx].attrs['data-date']
                frame = stamp, background_img1, background_img2, imgs2[idx].attrs['src'], imgs1[idx].attrs['src']
                self.frames.append(frame)

        except Exception, err:
            pass

    def all(self):
        return '\n'.join(self.frames)

    def now(self):
        frame = self.frames[0]

        p = tempfile.gettempdir()
        with Downloader() as d:
            f1 = d.download_file(p, frame[1])
            f2 = d.download_file(p, frame[2])
            f3 = d.download_file(p, frame[3])
            f4 = d.download_file(p, frame[4])


            background = Image.open(f1)
            foreground = Image.open(f2)
            map1 = Image.open(f3)
            map2 = Image.open(f4)


            #background.show()


        return frame[0] + '\n' + 'https:' + ''


class BetaMap(BetaGisMeteoPage):
    def __init__(self, region, maptype):
        BetaGisMeteoPage.__init__(self, '/maps/' + region + '/' + maptype + '/')
        self.name = ''

    def now(self):


        return self.name + '\n' + BetaGisMeteoPage.now(self)


# =============================================================================


def test():
    m = BetaMap(EUROPE, TEMPERATURE)
    m.update()


    t = m.now()