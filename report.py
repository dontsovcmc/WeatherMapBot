__author__ = 'dontsov'

import sys
from UniversalAnalytics import Tracker
from logger import log

class RTracker():
    def __init__(self, track_id, client_id):
        self.tracker = Tracker.create(track_id, client_id=client_id)
        log.info('tracker: create tracker for user=%s' % client_id)

    def track_event(self, category, action):
        self.tracker.send('event', category, action)

    def track_path(self, path, title):
        self.tracker.send('pageview', path=path, title=title)

    def track_screen(self, screenName):
        self.tracker.send('screenview', appName='WeatherMapBot', screenName=screenName, appVersion='0.1')

class ReportTrackers():

    def __init__(self):
        self.TRACK_ID = ''
        self.trackers = {}

    def add_tracker(self, client_id):
        self.trackers[str(client_id)] = RTracker(self.TRACK_ID, client_id)

    def remove_tracker(self, client_id):
        if str(client_id) in self.trackers:
            del self.trackers[str(client_id)]

    def track_event(self, client_id, category, action):
        log.info('track_event %s: %s %s' % (client_id, category, action))

        if not self.TRACK_ID: return
        if not str(client_id) in self.trackers:
            self.add_tracker(client_id)
        self.trackers[str(client_id)].track_event(category, action)

    def track_path(self, client_id, path, title):
        log.info('track_path %s: %s %s' % (client_id, path, title))
        if not self.TRACK_ID: return
        if not str(client_id) in self.trackers:
            self.add_tracker(client_id)
        self.trackers[str(client_id)].track_path(path, title)

    def tack_screen(self, client_id, screenName):
        log.info('track_screen %s: %s' % (client_id, screenName))

        if not self.TRACK_ID: return
        if not str(client_id) in self.trackers:
            self.add_tracker(client_id)
        self.trackers[str(client_id)].track_screen(screenName)


report = ReportTrackers()

if len(sys.argv) > 2:
    report.TRACK_ID = sys.argv[2]

#rk = RTracker(report.TRACK_ID, 0)
#rk.track_path('url1', 'title1')
#rk.track_screen('screen1')