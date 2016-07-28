# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys
from report import report
from bot import main

if __name__ == "__main__":

    if len(sys.argv) > 2:
        report.TRACK_ID = sys.argv[2]

    hook = len(sys.argv) > 3
    main(hook)