#!/usr/bin/env python
# encoding: utf-8
#    Copyright 2014 Tobias Mueller <muelli@cryptobitch.de>
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

from datetime import datetime
import signal
import sys
import argparse
import logging

from gi.repository import Gtk, GLib
from gi.repository import GObject

from monkeysign.gpg import Keyring

# These are relative imports
from __init__ import __version__

# FIXME: This should move to this file here
from SignPages import KeyPresentPage

log = logging.getLogger()



class KeyPresent(Gtk.Application):
    """A demo application showing how to display sufficient details
    about a key such that it can be sent securely.
    
    Note that the main purpose is to enable secure transfer, not
    reviewing key details.  As such, the implementation might change
    a lot, depending on the method of secure transfer.
    """
    def __init__(self, *args, **kwargs):
        #super(Keys, self).__init__(*args, **kwargs)
        Gtk.Application.__init__(
            self, application_id="org.gnome.keysign.keypresent")
        self.connect("activate", self.on_activate)
        self.connect("startup", self.on_startup)

        self.log = logging.getLogger()

        self.key_present_page = None


    def on_quit(self, app, param=None):
        self.quit()


    def on_startup(self, app):
        self.log.info("Startup")
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_title ("Keysign - Key")
        self.window.add(self.key_present_page)


    def on_activate(self, app):
        self.log.info("Activate!")
        #self.window = Gtk.ApplicationWindow(application=app)

        self.window.show_all()
        # In case the user runs the application a second time,
        # we raise the existing window.
        self.window.present()


    def run(self, args):
        log.debug("running: %s", args)
        fpr = args

        self.key_present_page = KeyPresentPage(fpr=fpr)

        super(KeyPresent, self).run()


def parse_command_line(argv):
    """Parse command line argument. See -h option

    :param argv: arguments on the command line must include caller file name.
    """
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description='Auxiliary helper program '+
                                                 'to present a key',
                                     formatter_class=formatter_class)
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(__version__))
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    #parser.add_argument("-g", "--gpg",
    #                    action="store_true", default=False,
    #                    help="Use local GnuPG Keyring instead of file.")
    #parser.add_argument('-o', metavar="output",
    #                    type=argparse.FileType('w'), default=sys.stdout,
    #                    help="redirect output to a file")
    #parser.add_argument('file', help='File to read keydata from ' +
    #                                 '(or KeyID if --gpg is given)')
    parser.add_argument('fpr', help='The fingerprint of the key to transfer')
    ## nargs='+', # argparse.REMAINDER,
    #parser.add_argument('input', metavar="input",
    ## nargs='+', # argparse.REMAINDER,
    #help="input if any...")
    arguments = parser.parse_args(argv[1:])
    # Sets log level to WARN going more verbose for each new -v.
    log.setLevel(max(3 - arguments.verbose_count, 0) * 10)
    return arguments


def main(args=sys.argv):
    """This is an example program of how to use the PresentKey widget"""
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(name)s (%(levelname)s): %(message)s')
    try:
        arguments = parse_command_line(args)
        
        #if arguments.gpg:
        #    keyid = arguments.file
        #    keyring = Keyring()
        #    # this is a dict {fpr: key-instance}
        #    found_keys = keyring.get_keys(keyid)
        #    # We take the first item we found and export the actual keydata
        #    fpr = found_keys.items()[0][0]
        #    keyring.export_data(fpr=fpr, secret=False)
        #    keydata = keyring.context.stdout
        #else:
        #    keydata = open(arguments.file, 'r').read()
        fpr = arguments.fpr

        app = KeyPresent()
        try:
            GLib.unix_signal_add_full(GLib.PRIORITY_HIGH, signal.SIGINT, lambda *args : app.quit(), None)
        except AttributeError:
            pass
    
        exit_status = app.run(fpr)
    
        return exit_status

        
    finally:
        logging.shutdown()

if __name__ == "__main__":
    sys.exit(main())
