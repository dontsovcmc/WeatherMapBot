# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys

from bot import main_hook

if len(sys.argv[1].split(' ')) > 1:
    args = sys.argv[1].split(' ')
    for i in range(0, len(args)):
        sys.argv[i+1] = args[0]

if __name__ == "__main__":
    main_hook()