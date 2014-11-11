#!/usr/bin/env python

import keysign
import logging

from sys import exit, stderr
from signal import SIGINT
from gi.repository import GLib

from keysign.MainWindow import MainWindow

class GnomeKeysign(object):
    LOGGING_FORMAT = '%(name)s (%(levelname)s): %(message)s'

    def __init__(self, logging_level = logging.DEBUG):
        # Initialize logging
        logging.basicConfig(stream=stderr, level=logging_level, format=self.LOGGING_FORMAT)

    def run(self):
        application = MainWindow()

        try:
            GLib.unix_signal_add_full(GLib.PRIORITY_HIGH, SIGINT, lambda *args : application.quit(), None)
        except AttributeError:
            pass

        return application.run(None)

if __name__ == '__main__':
    exit(GnomeKeysign().run())
