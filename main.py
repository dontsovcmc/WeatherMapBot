# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

from GisMeteoBot import start
from GisMeteoParser import Map

if __name__ == "__main__":

    m = Map('dgasgsdg', '/map/568/')
    m.update()
    t = m.now()

    start()