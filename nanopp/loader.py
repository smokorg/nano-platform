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
from abc import abstractclassmethod, abstractmethod
from importlib.abc import SourceLoader
import re
import threading
import sys
from nanopp.resources import ProtocolHandler

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
        self.loader_entries.append(loader_entry)

    def add_restricted_paths(self, path_patterns):
        self.add_loader(LoaderEntry(RestrictedEntryLoader(), path_patterns))


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

    @abstractmethod
    def create_context_for_this(self):
        pass

    def exec_module(self, module):
        module.__context__ = self.context
        extend(module.__dict__, self.get_overriden_globals())
        return SourceLoader.exec_module(self, module)

    def get_environ(self):
        return {}

    def get_overriden_globals(self):
        glb = {'__import__': create_context_sensitive_import(self.create_context_for_this())}
        env = self.get_environ()
        glb.update(env)
        return glb


class PlatformPluginsFinder(BaseFinder):

    def __init__(self, restricted_modules):
        super(PlatformPluginsFinder, self).__init__()
        self.plugins = {}
        restricted_modules = restricted_modules or []
        for restricted_path in restricted_modules:
            self.add_restricted_paths(restricted_path)

    def add_plugin(self, plugin_container):
        if self.plugins.get(plugin_container.plugin_id):
            raise Exception('Plugin %s already present' % plugin_container.plugin_id)
        loader_entries = self.create_loader_entries(plugin_container)
        self.plugins[plugin_container.plugin_id] = (loader_entries, plugin_container)
        for loader_entry in loader_entries:
            self.add_loader(loader_entry)

    def create_loader_entries(self, plugin_container):
        entries = []
        loader = self.create_loader(plugin_container)
        for export in plugin_container.manifest.exports:
            entries.append(export.name)

        return [LoaderEntry(loader=loader, path_patterns=entries)]

    def create_loader(self, plugin_container):
        return PluginLoader(plugin_container=plugin_container)

    def remove_plugin(self, plugin_id):
        loader_entries, plugin_container = self.plugins.get(plugin_id)
        if plugin_container:
            del self.plugins[plugin_id]

            for le in loader_entries:
                try:
                    self.loader_entries.remove(le)
                except ValueError:
                    pass


class PluginLoader(BaseLoader):

    def __init__(self, plugin_container):
        self.plugin_container = plugin_container

    def create_context_for_this(self):
        return self.plugin_container.plugin_id

    def get_filename(self, fullname):
        if not self.plugin_container.plugin.resource_exists(fullname):
            raise ImportError
        return fullname

    def get_data(self, path):
        if not self.plugin_container.plugin.resource_exist(path):
            return None

        return self.plugin_container.plugin.read_resource(path, True).read()

    def get_environ(self):
        return self.plugin_container.get_environ()


class ClassLoader:

    def __init__(self, import_fn):
        self.import_fn = import_fn

    def load_class(self, class_name):
        if not class_name:
            raise ValueError('Class name must be given')
        package, dot, clazz = class_name.rpartition('.')
        if not package:
            # FIXME: Research what happens if classes with no package are loaded
            raise ValueError('Unable to load top-level classes')
        loaded_module = self.import_fn(package, globals(), locals(), [clazz])
        if not loaded_module:
            raise Exception('Module not found: %s' % package)
        return getattr(loaded_module, clazz)


class ClassProtocolHandler(ProtocolHandler):

    def __init__(self, resource_loader):
        super(ClassProtocolHandler, self).__init__('class', resource_loader)
        self.class_loader = ClassLoader(import_fn=__import__)

    def load(self, path, *args, **kwargs):
        return self.class_loader.load_class(path)


def register_finder(finder):
    sys.meta_path.insert(0, finder)


def unregister_finder(finder):
    try:
        sys.meta_path.remove(finder)
    except ValueError:
        pass