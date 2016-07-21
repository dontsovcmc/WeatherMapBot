# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import httplib
import os

class Downloader(object):

    def __init__(self):
        self.conn = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        for k, v in self.conn.iteritems():
            v.close()

    def getresponse(self, url):
        '''
        :param path:
        :param url:  https://sdgdsdg/dgsgdsgs/file.png
        :return:
        '''
        http = url.split('://')[0]
        full_url = url.split('//')[1]
        server = full_url.split('/')[0]
        url = full_url[full_url.find('/'):]

        if not server in self.conn:
            if http == 'http':
                self.conn[server] = httplib.HTTPConnection(server)
            elif http == 'https':
                self.conn[server] = httplib.HTTPSConnection(server)

        conn = self.conn[server]

        conn.request('GET', url)
        r1 = conn.getresponse()
        return r1.read()

    def download_file(self, path, url):
        fname = url.split('/')[-1].split('?')[0]

        data = self.getresponse(url)

        filepath = os.path.join(path, fname)
        with open(filepath, 'wb') as f:
            f.write(data)
        return str(filepath)

