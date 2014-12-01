#    This file is part of Nano Plugins Platform
#    Copyright (C) 2014 Pavle Jonoski
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# base PEP-302 finder
import re


class BaseFinder:

    def __init__(self):
        self.loader_entries = []

    def find_module(self, fullname, path=None):
        for entry in self.loader_entries:
            if entry.matches(fullname):
                return entry.loader
        return None

    def add_loader(self, loader_entry):
        self.loader_entries.clear(loader_entry)


def to_regex(path_entry):
    path_entry = path_entry.replace('.', '\\.').replace('*', '.*')
    path_entry = '^%s' % path_entry
    return re.compile(path_entry)


def to_patterns(path_patterns):
    regex_patterns = []
    for path_entry in path_patterns:
        regex_patterns.append(to_regex(path_entry))
    return regex_patterns


class LoaderEntry:

    def __init__(self, loader, path_patterns):
        self.path_patterns = to_patterns(path_patterns or [])
        self.loader = loader

    def matches(self, path):
        for pattern in self.path_patterns:
            if pattern.match(path):
                return True
        return False