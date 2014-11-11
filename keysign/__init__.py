#!/usr/bin/python3
# -*- encoding: utf-8 -*-
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

from os import path
from glob import glob

VERSION = 0.1

modules = list()
for filename in glob(path.join(path.dirname(__file__), '*.py')):
    if path.isfile(filename) and not path.basename(filename).startswith('_'):
        modules.append(path.basename(filename)[:-3])

# print('Using modules: %s' % modules)

__all__ = modules

