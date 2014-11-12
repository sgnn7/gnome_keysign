#!/usr/bin/env python
#
#    Copyright 2014 Srdjan Grubor <sgnn7@sgnn7.org>
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
import monkeysign.gpg

class Logger(object):
    def __init__(self):
        self.logger = logging.getLogger()


        # Monkeypatching monkeysign to get more debug output
        original_build_command = monkeysign.gpg.Context.build_command
        def patched_build_command(*args, **kwargs):
            return_value = original_build_command(*args, **kwargs)

            self.debug("Building cmd: %s", ' '.join(return_value))

            return return_value

        monkeysign.gpg.Context.build_command = patched_build_command

    def debug(self, *args):
        self.logger.debug(args)

    def info(self, *args):
        self.logger.info(args)

# Singleton logger instance
def get_instance():
    if '__logger' not in vars():
        __logger = Logger()

    return __logger
