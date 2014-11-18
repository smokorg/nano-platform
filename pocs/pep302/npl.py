"""
Nano Platform Loaders
"""


# Finder/Loader
from importlib.abc import SourceLoader
import os
import threading
import sys


class NPLoader(SourceLoader):

    def __init__(self, context, packages=[], restricted=[]):
        self.context = context
        self.packages = packages
        self.restricted = restricted

    def get_filename(self, fullname):
        cwd = os.getcwd()
        filename = fullname.replace(".", os.sep)
        filename = os.path.realpath(cwd + os.sep + filename )
        if fullname in self.packages:
            return filename + os.sep + '__init__.py'
        else:
            return filename + '.py'

    def get_data(self, path):
        with open(path, 'r') as file:
            return file.read()
        return ""

    def exec_module(self, module):
        print(" > exec_module: %s" % module)
        module.__context__ = self.context
        module.__dict__["__import__"] = context_aware_import_factory(self.context)
        return SourceLoader.exec_module(self, module)

    def get_code(self, fullname):
        self.check_if_restricted(fullname)
        return SourceLoader.get_code(self, fullname)

    def check_if_restricted(self, fullname):
        if fullname in self.restricted:
            print(' !!! Restricted: %s' % fullname)
            raise ImportError('%s: loading restricted' % fullname, name=fullname)

class NPFinder:

    def __init__(self, tldata):
        self.tldata = tldata
        self.packages = ['testpkg', 'testpkg.subpkg', 'testpkg.subpkg2']
        self.modules = ['testpkg.testmod', 'testpkg.subpkg.testsubmod', 'testpkg.subpkg2.testsubmod2']
        self.restricted = ['testpkg.subpkg2', 'testpkg.subpkg.testsubmod']

    def find_module(self, fullname, path=None):
        print('import %s (%s)'%(fullname, path))
        self.print_curr_context()
        if fullname in self.packages or fullname in self.modules:
            print(' > known module/package')
            return NPLoader(context=fullname, packages=self.packages, restricted=self.restricted)
        else:
            print(' > Not known to this finder')
        return None

    def print_curr_context(self):
        try:
            print(' > Imported by: %s' % self.tldata.context)
        except:
            print("    -> Top level import (context not set)")

# keep the reference to the original import
original_import = __import__
tl = threading.local()

def context_aware_import_factory(context):
    def context_aware_import(*args, **kwargs):
        print("context_aware_import() args=%s; kwargs=%s" % (args, kwargs))
        tl.context = context
        return original_import(*args, **kwargs)
    return context_aware_import

# Register the hook
sys.meta_path.insert(0, NPFinder(tldata=tl))

# let's try to import something:

print(" --- LOADING CUSTOM MODULE ---")
import testpkg.testmod
print(" -----------------------------")

print(' --- LOADING RESTRICTED --- ')
# try loading restricted package

import testpkg.subpkg.testsubmod
