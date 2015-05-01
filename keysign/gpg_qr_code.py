#!/usr/bin/env python
#
#    Copyright 2014 Tobias Mueller <muelli@cryptobitch.de>
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

"""This is a very simple QR Code generator which scans your GnuPG keyring
for keys and selects the one matching your input
"""

import  sys

from gi.repository import Gtk
from monkeysign.gpg import Keyring

from QRCode import QRImage

class QRGenerator(object):
    def run(self, key):
        keys = Keyring().get_keys(key)

        # Heh, we take the first key here. Maybe we should raise a warning
        # or so, when there is more than one key.
        fpr = keys.items()[0][0]
        data = 'OPENPGP4FPR:' + fpr

        window = Gtk.Window()
        window.set_default_size(100,100)

        window.connect("delete-event", Gtk.main_quit)

        label = Gtk.Label(data)
        qr_code = QRImage(data)

        vbox = Gtk.VBox()
        vbox.add(label)
        vbox.add(qr_code)

        window.add(vbox)
        window.show_all()

        Gtk.main()

if __name__ == '__main__':
    QRGenerator().run(sys.argv[1])
