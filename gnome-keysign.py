#!/usr/bin/env python
# -*- encoding: utf-8 -*
#
#    Copyright 2014 Tobias Mueller <muelli@cryptobitch.de>,
#                   Srdjan Grubor <sgnn7@sgnn7.org>
#
#    This file is part of GNOME Keysign.
#
#    GNOME Keysign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GNOME Keysign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GNOME Keysign.  If not, see <http://www.gnu.org/licenses/>.

import logging

from sys import stderr
from signal import SIGINT
from gi.repository import GLib

from keysign.MainWindow import MainWindow

class GnomeKeysign(object):
    LOGGING_FORMAT = '%(name)s (%(levelname)s): %(message)s'

    def __init__(self, logging_level = logging.DEBUG):
        logging.basicConfig(stream = stderr,
                            level = logging_level,
                            format = self.LOGGING_FORMAT)
    def run(self):
        application = MainWindow()

        try:
            GLib.unix_signal_add_full(GLib.PRIORITY_HIGH,
                                      SIGINT,
                                      lambda *args : application.quit(),
                                      None)
        except AttributeError:
            pass

        return application.run(None)

if __name__ == '__main__':
    exit(GnomeKeysign().run())
