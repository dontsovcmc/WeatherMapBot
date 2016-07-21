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