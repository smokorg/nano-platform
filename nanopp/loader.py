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
from importlib.abc import SourceLoader
import re
import threading

__local_context = threading.local()
__original_import__ = __import__

# constants
IMPORT_CONTEXT = "nanopp.IMPORT_CONTEXT"


def put_to_context(key, value):
    __local_context[key] = value


def get_from_context(key):
    try:
        return __local_context[key]
    except KeyError:
        return None


def extend(dict_a, dict_b):
    for k, v in dict_b.items():
        dict_a[k] = v

def create_context_sensitive_import(context):
    """ Creates context sensitive import function to be used as replacement for the __import__ builtin.
    :param context: the context to be set when calling __import__
    :return: the replacement, context-setting import
    """
    def context_sensitive_import(*args, **kwargs):
        """ Context sensitive and setting import.
        Sets a predefined context in thread local, just before calling and passing control to the Python's
        builtin __import__
        :return: the imported module
        """
        put_to_context(IMPORT_CONTEXT, context)
        return __original_import__(*args, **kwargs)
    return context_sensitive_import


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


class RestrictedEntryLoader:

    def load_module(self):
        raise ImportError


class BaseLoader(SourceLoader):

    def __init__(self):
        SourceLoader.__init__(self)

    def get_current_context(self):
        return get_from_context(IMPORT_CONTEXT)

    def create_context_for_this(self):
        pass

    def exec_module(self, module):
        module.__context__ = self.context
        extend(module.__dict__, self.get_overriden_globals())
        return SourceLoader.exec_module(self, module)

    def get_overriden_globals(self):
        glb = {}
        glb['__import__'] = create_context_sensitive_import(self.create_context_for_this())
        return glb
