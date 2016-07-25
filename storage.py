# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import tempfile
import os

from network import Downloader
from logger import log

class FileStorage(object):

    def __init__(self):
        self.files = {}
        self.work_dir = tempfile.gettempdir()
        
    def get(self, url, force=False):
        if url in self.files and not force:
            log.info('FileStorage: file here %s' % self.files[url])
            return self.files[url]

        with Downloader() as d:
            path = d.download_file(self.work_dir, url)
        self.files[url] = path
        log.info('FileStorage: file downloaded to %s' % path)
        return path

    def download(self, url, map_id, timestamp):
        root = self.work_dir
        path = os.path.join(root, str(map_id), os.path.normpath(timestamp.strftime('%Y/%m/%d')))
        fname = timestamp.strftime('%Y-%m-%d_%H-%M')

        if not os.path.isdir(path):
            os.makedirs(path)

        with Downloader() as d:
            path = d.download_file(path, url, fname)
        return path

file_storage = FileStorage()

import shelve

shelve_name = 'shelve.db'

# States are saved in a dict that maps chat_id -> state
#state = dict()

# Информация о пользователе:
# ( user_id, выбранный сайт, выбранная карта )
#context = dict()

class Shelve(object):

    def __init__(self):
        self.storage = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.storage = shelve.open(shelve_name)

    def close(self):
        self.storage.close()

    def set(self, chat_id, field, value):
        self.storage[str(chat_id) + field] = value

    def get(self, chat_id, field, default=None):
        try:
            return self.storage[str(chat_id) + field]
        except KeyError:
            return default

