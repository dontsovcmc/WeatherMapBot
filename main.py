# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys

from bot import main, main_hook
from report import report

if __name__ == "__main__":

    if len(sys.argv) > 2:
        print 'argv1: %s' % sys.argv[1]
        report.TRACK_ID = sys.argv[2]
        main()
    elif len(sys.argv) > 3:
        print 'argv1: %s' % sys.argv[1]
        print 'argv2: %s' % sys.argv[2]
        report.TRACK_ID = sys.argv[2]
        main_hook()
    else:
        main()