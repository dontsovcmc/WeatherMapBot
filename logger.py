# -*- coding: utf-8 -*-
__author__ = 'dontsov'

import logging
import sys
from datetime import datetime

class Logger(object):
    def __init__(self):
        log = logging.getLogger('')
        log.setLevel(logging.INFO)

        filename = datetime.now().strftime('wmb_%d.%m.%Y_%H.%M.log')
        fh = logging.FileHandler(filename, mode='w')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        log.addHandler(fh)

        # Задействовать консоль для вывода лога
        console = sys.stderr
        if console is not None:
            # Вывод лога производится и на консоль и в файл (одновременно)
            console = logging.StreamHandler(console)
            console.setLevel(logging.INFO)
            console.setFormatter(formatter)
            log.addHandler(console)

Logger()

log = logging.getLogger('')