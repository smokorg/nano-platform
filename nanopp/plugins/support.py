__author__ = 'pavle'

"""
Plugin structure:
 <plugin_root>:
    + PLUGIN.MF - Plugin manifest
"""


class Entry:

    def __init__(self, entry_name, is_package=False):
        self.name = entry_name
        self.is_package = is_package


class ExportsEntry(Entry):

    def __init__(self, entry_name, export_version, is_package=False):
        Entry.__init__(self, entry_name, is_package)
        self.version = export_version


def check_min_version(version, min_version, incl):
    if min_version is None:
        return True
    else:
        if incl:
            return version >= min_version
        else:
            return version > min_version


def check_max_version(version, max_version, incl):
    if max_version is None:
        return True
    else:
        if incl:
            return version <= max_version
        else:
            return version < max_version


def normalize_version(version_tpl):
    version, incl = version_tpl if isinstance(version_tpl, tuple) else (version_tpl, False)
    return normalize_version_string(version), incl


def normalize_version_string(version):
    if version is None:
        return None
    vrs = version.split('.')

    if len(vrs) < 3:
        n = 3 - len(vrs)
        while n:
            vrs.append('0')
            n -= 1
        version = '.'.join(vrs)

    return version


class RequiresEntry(Entry):

    @staticmethod
    def from_string(entry_string):
        pass

    def __init__(self, entry_name, version_range, is_package=False):
        Entry.__init__(self, entry_name, is_package)

        if version_range is None or len(version_range) == 0:
            version_range = [(None, False), (None, False)]
        if len(version_range) < 2:
            version_range.append((None, False))

        self.version_range = [normalize_version(version_range[0]), normalize_version(version_range[1])]

    def version_in_range(self, version):
        min_version, min_inclusive = self.version_range[0]
        max_version, max_inclusive = self.version_range[1]

        return check_min_version(version, min_version, min_inclusive) and \
            check_max_version(version, max_version, max_inclusive)


class PluginManifest:

    def __init__(self):
        self.requires = []
        self.exports = []

class PluginResource:

    def __init__(self):
        pass

    def get_manifest(self):
        pass

    def read_resource(self, resource_path):
        pass
