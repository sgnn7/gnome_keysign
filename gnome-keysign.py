#!/usr/bin/env python

import logging
import sys
import signal

from gi.repository import GLib

from keysign.MainWindow import MainWindow

logging.basicConfig(stream=sys.stderr,
                    level=logging.DEBUG,
                    format='%(name)s (%(levelname)s): %(message)s')

def main():
    app = MainWindow()

    try:
        GLib.unix_signal_add_full(GLib.PRIORITY_HIGH,
                                  signal.SIGINT,
                                  lambda *args : app.quit(),
                                  None)
    except AttributeError:
        pass

    exit_status = app.run(None)
    return exit_status

sys.exit(main())
