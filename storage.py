# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import tempfile

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

file_storage = FileStorage()

import shelve

shelve_name = 'shelve.db'

# States are saved in a dict that maps chat_id -> state
#state = dict()

# Информация о пользователе:
# ( user_id, выбранный сайт, выбранная карта )
#context = dict()

def shelve_get(chat_id, field, default):
    storage = shelve.open(shelve_name)
    try:
        answer = storage[str(chat_id) + field]
        storage.close()
        return answer
    except KeyError:
        storage.close()
        return default


def shelve_set(chat_id, field, value):
    storage = shelve.open(shelve_name)
    storage[str(chat_id) + field] = value
    storage.close()

