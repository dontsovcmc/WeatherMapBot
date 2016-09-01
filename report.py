# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from UniversalAnalytics import Tracker
from logger import log

APP_VERSION = "0.2"


class RTracker(object):
    def __init__(self, track_id, client_id):
        self.client_id = client_id
        self.tracker = Tracker.create(track_id, client_id=client_id)
        log.info('tracker: create tracker for user=%s' % client_id)

    def track_event(self, category, action):
        log.info('track_event %s: %s\t%s' % (self.client_id, category, action))
        self.tracker.send('event', category, action)

    def track_path(self, path, title):
        log.info('track_path %s: %s\t%s' % (self.client_id, path, title))
        self.tracker.send('pageview', path=path, title=title)

    def track_screen(self, screenName):
        log.info('track_screen %s: %s' % (self.client_id, screenName))
        self.tracker.send('screenview', appName='WeatherMapBot', screenName=screenName, appVersion=APP_VERSION)


class ReportTrackers(object):

    def __init__(self):
        self.TRACK_ID = ''
        self.trackers = {}

    def add_tracker(self, client_id):
        self.trackers[str(client_id)] = RTracker(self.TRACK_ID, client_id)

    def remove_tracker(self, client_id):
        if str(client_id) in self.trackers:
            del self.trackers[str(client_id)]

    def track_event(self, client_id, category, action):
        if not self.TRACK_ID:
            return
        if not str(client_id) in self.trackers: self.add_tracker(client_id)

        self.trackers[str(client_id)].track_event(category, action)

    def track_path(self, client_id, path, title):
        if not self.TRACK_ID:
            return
        if not str(client_id) in self.trackers: self.add_tracker(client_id)

        self.trackers[str(client_id)].track_path(path, title)

    def track_screen(self, client_id, screenName):
        if not self.TRACK_ID:
            return
        if not str(client_id) in self.trackers: self.add_tracker(client_id)

        self.trackers[str(client_id)].track_screen(screenName)

report = ReportTrackers()
