#!/usr/bin/env python
#    Copyright 2014 Andrei Macavei <andrei.macavei89@gmail.com>
#    Copyright 2014 Tobias Mueller <muelli@cryptobitch.de>
#    Copyright 2014 Srdjan GRubor <sgnn7@sgnn7.org>
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

import sys
import logging
import StringIO

from itertools import islice
from datetime import datetime

from gi.repository import Gtk, GLib, GdkPixbuf
from monkeysign.gpg import Keyring
from scan_barcode import BarcodeReaderGTK
from qrencode import encode_scaled
from qr_code import QRImage

from utils import parse_sig_list, signatures_for_keyid

log = logging.getLogger()

# Pages for 'Keys' Tab
class KeysPage(Gtk.VBox):
    def __init__(self, key_section):
        super(KeysPage, self).__init__()

        # pass a reference to KeySignSection in order to access its widgets
        self.key_section = key_section

        # set up the list store to be filled up with user's gpg keys
        self.store = Gtk.ListStore(str, str, str)

        # FIXME: this should be moved to KeySignSection
        self.keyring = Keyring() # the user's keyring

        self.keys_dict = {}

        # FIXME: this should be a callback function to update the display
        # when a key is changed/deleted
        for key in self.keyring.get_keys(None, True, False).values():
            if key.invalid or key.disabled or key.expired or key.revoked:
                continue

            uidslist = key.uidslist #UIDs: Real Name (Comment) <email@address>
            keyid = str(key.keyid()) # the key's short id

            if not keyid in self.keys_dict:
                self.keys_dict[keyid] = key

            for e in uidslist:
                uid = str(e.uid)
                # remove the comment from UID (if it exists)
                com_start = uid.find('(')
                if com_start != -1:
                    com_end = uid.find(')')
                    uid = uid[:com_start].strip() + uid[com_end+1:].strip()

                # split into user's name and email
                tokens = uid.split('<')
                name = tokens[0].strip()
                email = 'unknown'
                if len(tokens) > 1:
                    email = tokens[1].replace('>','').strip()

                self.store.append((name, email, keyid))

        # create the tree view
        self.tree_view = Gtk.TreeView(model=self.store)

        # setup 'Name' column
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn("Name", name_renderer, text=0)

        # setup 'Email' column
        email_renderer = Gtk.CellRendererText()
        email_column = Gtk.TreeViewColumn("Email", email_renderer, text=1)

        # setup 'Key' column
        key_renderer = Gtk.CellRendererText()
        key_column = Gtk.TreeViewColumn("Key", key_renderer, text=2)

        self.tree_view.append_column(name_column)
        self.tree_view.append_column(email_column)
        self.tree_view.append_column(key_column)

        # make the tree view resposive to single click selection
        self.tree_view.get_selection().connect('changed', self.on_selection_changed)

        # make the tree view scrollable
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.tree_view)
        self.scrolled_window.set_min_content_height(200)

        self.pack_start(self.scrolled_window, True, True, 0)

    def on_selection_changed(self, *args):
        self.key_section.nextButton.set_sensitive(True)

class KeyPresentPage(Gtk.HBox):
    def __init__(self):
        super(KeyPresentPage, self).__init__()

        # create left side Key labels
        left_top_label = Gtk.Label()
        left_top_label.set_markup('<span size="15000">' + 'Key Fingerprint' + '</span>')

        self.fingerprint_label = Gtk.Label()
        self.fingerprint_label.set_selectable(True)

        # left vertical box
        left_vbox = Gtk.VBox(spacing=10)
        left_vbox.pack_start(left_top_label, False, False, 0)
        left_vbox.pack_start(self.fingerprint_label, False, False, 0)

        self.pixbuf = None # Hold QR code in pixbuf
        self.fpr = None # The fpr of the key selected to sign with

        # display QR code on the right side
        qrcode_label = Gtk.Label()
        qrcode_label.set_markup('<span size="15000">' + 'Fingerprint QR code' + '</span>')

        self.qrcode = QRImage()
        self.qrcode.props.margin = 10

        # right vertical box
        self.right_vbox = Gtk.VBox(spacing=10)
        self.right_vbox.pack_start(qrcode_label, False, False, 0)
        self.right_vbox.pack_start(self.qrcode, True, True, 0)

        self.pack_start(left_vbox, True, True, 0)
        self.pack_start(self.right_vbox, True, True, 0)

    def display_fingerprint_qr_page(self, openPgpKey):
        rawfpr = openPgpKey.fpr
        self.fpr = rawfpr
        # display a clean version of the fingerprint
        fpr = ""
        for i in xrange(0, len(rawfpr), 4):

            fpr += rawfpr[i:i+4]
            if i != 0 and (i+4) % 20 == 0:
                fpr += "\n"
            else:
                fpr += " "

        fpr = fpr.rstrip()
        self.fingerprint_label.set_markup('<span size="20000">' + fpr + '</span>')

        # draw qr code for this fingerprint
        self.draw_qrcode()

    def draw_qrcode(self):
        assert self.fpr
        data = 'OPENPGP4FPR:' + self.fpr
        self.qrcode.data = data

class KeyDetailsPage(Gtk.VBox):
    def __init__(self):
        super(KeyDetailsPage, self).__init__()
        self.set_spacing(10)
        self.log = logging.getLogger()

        # FIXME: this should be moved to KeySignSection
        self.keyring = Keyring()

        uids_label = Gtk.Label()
        uids_label.set_text("UIDs")

        # this will later be populated with uids when user selects a key
        self.uids_box = Gtk.VBox(spacing=5)

        self.expire_label = Gtk.Label()
        self.expire_label.set_text("Expires 0000-00-00")

        self.signatures_label = signatures_label = Gtk.Label()
        signatures_label.set_text("Signatures")

        # this will also be populated later
        self.signatures_box = Gtk.VBox(spacing=5)

        self.pack_start(uids_label, False, False, 0)
        self.pack_start(self.uids_box, True, True, 0)
        self.pack_start(self.expire_label, False, False, 0)
        self.pack_start(signatures_label, False, False, 0)
        self.pack_start(self.signatures_box, True, True, 0)

    def display_uids_signatures_page(self, openPgpKey):
        # destroy previous uids
        for uid in self.uids_box.get_children():
            self.uids_box.remove(uid)
        for sig in self.signatures_box.get_children():
            self.signatures_box.remove(sig)

        # display a list of uids
        labels = []
        for uid in openPgpKey.uidslist:
            label = Gtk.Label(str(uid.uid))
            label.set_line_wrap(True)
            labels.append(label)

        for label in labels:
            self.uids_box.pack_start(label, False, False, 0)
            label.show()

        try:
            exp_date = datetime.fromtimestamp(float(openPgpKey.expiry))
            expiry = "Expires {:%Y-%m-%d %H:%M:%S}".format(exp_date)
        except ValueError, e:
            expiry = "No expiration date"

        self.expire_label.set_markup(expiry)


        ### Set up signatures
        keyid = str(openPgpKey.keyid())
        sigslist = signatures_for_keyid(keyid)

        SHOW_SIGNATURES = False
        if not SHOW_SIGNATURES:
            self.signatures_label.hide()
        else:
            self.signatures_label.show()
            sorted_sigslist = sorted(sigslist,
                                     key=lambda signature:signature[1],
                                     reverse=True)
            for (keyid,timestamp,uid) in islice(sorted_sigslist, 10):
                signature_label = Gtk.Label()
                date = datetime.fromtimestamp(float(timestamp))
                signature_label.set_markup(str(keyid) + "\t\t" + date.ctime())
                signature_label.set_line_wrap(True)

                self.signatures_box.pack_start(signature_label, False, False, 0)
                signature_label.show()

        signature_label = Gtk.Label()
        signature_label.set_markup("%d signatures" % len(sigslist))
        signature_label.set_line_wrap(True)
        self.signatures_box.pack_start(signature_label, False, False, 0)
        signature_label.show()

# Pages for "Get Key" Tab
class ScanFingerprintPage(Gtk.HBox):
    def __init__(self):
        super(ScanFingerprintPage, self).__init__()
        self.set_spacing(10)

        # set up labels
        left_label = Gtk.Label()
        left_label.set_markup('Type fingerprint')
        right_label = Gtk.Label()
        right_label.set_markup('... or scan QR code')

        # set up text editor
        self.text_view = Gtk.TextView()
        self.text_buffer = self.text_view.get_buffer()

        # set up scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.text_view)

        # set up webcam frame
        self.scan_frame = Gtk.Frame(label='QR Scanner')
        self.scan_frame = BarcodeReaderGTK()
        self.scan_frame.set_size_request(150,150)
        self.scan_frame.show()

        # set up load button: this will be used to load a qr code from a file
        self.load_button = Gtk.Button('Open Image')
        self.load_button.set_image(Gtk.Image.new_from_icon_name('gtk-open', Gtk.IconSize.BUTTON))
        self.load_button.connect('clicked', self.on_loadbutton_clicked)
        self.load_button.set_always_show_image(True)

        # set up left box
        left_box = Gtk.VBox(spacing=10)
        left_box.pack_start(left_label, False, False, 0)
        left_box.pack_start(scrolled_window, True, True, 0)

        # set up right box
        right_box = Gtk.VBox(spacing=10)
        right_box.pack_start(right_label, False, False, 0)
        right_box.pack_start(self.scan_frame, True, True, 0)
        right_box.pack_start(self.load_button, False, False, 0)

        # pack up
        self.pack_start(left_box, True, True, 0)
        self.pack_start(right_box, True, True, 0)

    def get_text_from_text_view(self):
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        raw_text = self.text_buffer.get_text(start_iter, end_iter, False)

        self.text_buffer.delete(start_iter, end_iter)
        # return raw input from user. It will be checked on higher
        # level if the there was a fingerprint entered
        return raw_text

    def on_loadbutton_clicked(self, *args, **kwargs):
        print("load")

class SignKeyPage(Gtk.VBox):
    def __init__(self):
        super(SignKeyPage, self).__init__()
        self.set_spacing(5)

        self.main_label = Gtk.Label()
        self.main_label.set_line_wrap(True)

        self.pack_start(self.main_label, False, False, 0)

    def display_downloaded_key(self, key, scanned_fpr):
        # FIXME: If the two fingerprints don't match, the button
        # should be disabled
        key_text = GLib.markup_escape_text(str(key))

        markup = """\


Signing the following key

<b>{0}</b>

Press 'Next' if you have checked the ID of the person
and you want to sign all UIDs on this key.""".format(key_text)

        self.main_label.set_markup(markup)
        self.main_label.show()

class PostSignPage(Gtk.VBox):
    def __init__(self):
        super(PostSignPage, self).__init__()
        self.set_spacing(10)

        # setup the label
        signed_label = Gtk.Label()
        signed_label.set_text('The key was signed and an email was sent to key owner! What next?')

        # setup the buttons
        send_back_button = Gtk.Button('   Resend email   ')
        send_back_button.set_image(Gtk.Image.new_from_icon_name("gtk-network", Gtk.IconSize.BUTTON))
        send_back_button.set_always_show_image(True)
        send_back_button.set_halign(Gtk.Align.CENTER)

        saveButton = Gtk.Button(' Save key locally ')
        saveButton.set_image(Gtk.Image.new_from_icon_name("gtk-save", Gtk.IconSize.BUTTON))
        saveButton.set_always_show_image(True)
        saveButton.set_halign(Gtk.Align.CENTER)

        email_button = Gtk.Button('Revoke signature')
        email_button.set_image(Gtk.Image.new_from_icon_name("gtk-clear", Gtk.IconSize.BUTTON))
        email_button.set_always_show_image(True)
        email_button.set_halign(Gtk.Align.CENTER)

        # pack them into a container for alignment
        container = Gtk.VBox(spacing=3)
        container.pack_start(signed_label, False, False, 5)
        container.pack_start(send_back_button, False, False, 0)
        container.pack_start(saveButton, False, False, 0)
        container.pack_start(email_button, False, False, 0)
        container.set_valign(Gtk.Align.CENTER)

        self.pack_start(container, True, False, 0)
