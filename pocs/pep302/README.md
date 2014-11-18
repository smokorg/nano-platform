PEP 302 Finder/Loader Proof-Of-Concept
--------------------------------------

POC Goals:

 * Import from a custom location, not in python path
 * Context-aware import - which module does the actual import
 * PEP-302 Finder
 * PEP-302 Loader
 * builtin function ```__import__``` can be replaced in the loaded modules, thus giving control over ```import``` and ```from-import``` statements
 * Restricting certain packages to be loaded
 * Restricting some modules to load certain packages
 
Import from a custom location, not in python path
-------------------------------------------------

This is possible by registering a **finder** in ```sys.meta_path```.

More details on how the actual protocol looks like are available in PEP-302:

https://www.python.org/dev/peps/pep-0302

The actual Finder/Loader:

Check the file **npl.py** for the full implementation in __pocs/pep302/__

```
#!python

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

```