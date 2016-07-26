# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from fabric.api import local, settings, abort, run, cd
from fabric.contrib.console import confirm

def push(commit='unknown'):
    local("git add -u")
    local("git commit -m %s" % commit)
    local("git push origin master")


def update():
    local("git fetch")
    local("git rebase origin/master")
