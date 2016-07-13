__author__ = 'doncov.eugene'

from telegram import KeyboardButton

class WeatherMap(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def update(self):
        pass

    def now(self):
        pass


class WeatherSite():
    def __init__(self, name, maps):
        '''
        name = name for menu button
        maps = list of WeatherMap
        '''
        self.name = name
        self.maps = maps

    def get(self, name):
        found = [m for m in self.maps if m.name == name]
        if found:
            return found[0]

    def keyboard_layout(self):
        def add_kb(maps):
            return [KeyboardButton(m.name) for m in maps]
        return [add_kb(self.maps[x:x+3]) for x in xrange(0, len(self.maps), 3)]


class WeatherSites():
    def __init__(self, sites):
        self.sites = sites

    def get(self, name):
        found = [s for s in self.sites if s.name == name]
        if found:
            return found[0]

    def keyboard_layout(self):
        def add_kb(maps):
            return [KeyboardButton(m.name) for m in maps]
        return [add_kb(self.sites[x:x+3]) for x in xrange(0, len(self.sites), 3)]