# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys

from bot import main, main_hook

if __name__ == "__main__":

    if len(sys.argv) > 2:
        main_hook()
    else:
        main()