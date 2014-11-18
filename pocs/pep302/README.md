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

Here is what an example implementation might look like

```python


"""
The finder object.
An instance of this objest is to be prepended to the sys.meta_path array
"""
class NPFinder:

    def __init__(self, tldata):
        # this is the thread-local context data holder
        self.tldata = tldata 
        
        # which packages
        self.packages = ['testpkg', 'testpkg.subpkg', 'testpkg.subpkg2']
        
        # which subpackages we're handling
        self.modules = ['testpkg.testmod', 'testpkg.subpkg.testsubmod', 'testpkg.subpkg2.testsubmod2']
        
        # and what is restricted
        self.restricted = ['testpkg.subpkg2', 'testpkg.subpkg.testsubmod']

    '''
    Performs the actual search for the module.
    We do the following here:
        1. Check if the requested module/package is one of the registered that we handle
        2. If it is, the return the actual loader for that package/module
        3. If not, return None, meaning we do not handle it, but maybe someone else does
    '''
    def find_module(self, fullname, path=None):
        print('import %s (%s)'%(fullname, path))
        self.print_curr_context()
        if fullname in self.packages or fullname in self.modules:
            print(' > known module/package')
            return NPLoader(context=fullname, packages=self.packages, restricted=self.restricted)
        else:
            print(' > Not known to this finder')
        return None
    
    '''
    Prints out the current data set in thread local.
    This is actually the name of the module where the actual "import" statement is.
    '''
    def print_curr_context(self):
        try:
            print(' > Imported by: %s' % self.tldata.context)
        except:
            print("    -> Top level import (context not set)")



"""
This is the actual loader.
It is based on SourceLoader for the sake of simplicity.
"""
class NPLoader(SourceLoader):
    
    
    """Constructor.
    Params:
    
        :context - thread local context data. In this implementation this is the name of the module which imports the
        requested module/package.
        :packages - list of all packages that we handle, just so we can quickly determine if the "fullname" is a package
        or a module.
        :restricted - list of restricted packages/modules.
    """
    def __init__(self, context, packages=[], restricted=[]):
        self.context = context
        self.packages = packages
        self.restricted = restricted

    """Translates the fullname (dotted representation of the package/module) to an actual Python script file
    """
    def get_filename(self, fullname):
        cwd = os.getcwd()
        filename = fullname.replace(".", os.sep)
        filename = os.path.realpath(cwd + os.sep + filename )
        if fullname in self.packages:
            return filename + os.sep + '__init__.py'
        else:
            return filename + '.py'

    """Returns the content of the python code file
    """
    def get_data(self, path):
        with open(path, 'r') as file:
            return file.read()
        return ""
    
    """Executes and loads the module.
    """
    def exec_module(self, module):
        print(" > exec_module: %s" % module)
        module.__context__ = self.context
        
        # This is where we override the __import__ function for this module.
        # Every "import" or "from...import" statement will be translated to a __import__ call, and we're
        # replacing the original __import__ with our own implementation. This way, we actually control the
        # imports from this module.
        module.__dict__["__import__"] = context_aware_import_factory(self.context)
        return SourceLoader.exec_module(self, module)
    
    """Checks if the mod/pkg is not restricted and if not, passes to the super-implementation.
    """
    def get_code(self, fullname):
        self.check_if_restricted(fullname)
        return SourceLoader.get_code(self, fullname)

    """ Check if the mod/pkg is restricted. If it is, raises an ImportError
    """
    def check_if_restricted(self, fullname):
        if fullname in self.restricted:
            print(' !!! Restricted: %s' % fullname)
            raise ImportError('%s: loading restricted' % fullname, name=fullname)


# keep the reference to the original import
original_import = __import__

# Create thread-local context data holder
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

```

If we run the above script we'll get an output as follows:

```
 --- LOADING CUSTOM MODULE ---
import testpkg (None)
    -> Top level import (context not set)
 > known module/package
 > exec_module: <module 'testpkg' from '/home/pavle/projects/python/xmpp-server/nano-platform/pocs/pep302/testpkg/__init__.py'>
import _bootlocale (None)
    -> Top level import (context not set)
 > Not known to this finder
import _locale (None)
    -> Top level import (context not set)
 > Not known to this finder
import testpkg.testmod (['/home/pavle/projects/python/xmpp-server/nano-platform/pocs/pep302/testpkg'])
    -> Top level import (context not set)
 > known module/package
 > exec_module: <module 'testpkg.testmod' from '/home/pavle/projects/python/xmpp-server/nano-platform/pocs/pep302/testpkg/testmod.py'>
import http (None)
    -> Top level import (context not set)
 > Not known to this finder
context_aware_import() args=('http.client',); kwargs={}
import http.client (['/usr/lib/python3.4/http'])
 > Imported by: testpkg.testmod
 > Not known to this finder
import email (None)

.
.
Lots of imports
.
.
import _ssl (None)
 > Imported by: testpkg.testmod
 > Not known to this finder

```

As seen, the import of ```http.client``` is done by the replaced ```__import__``` function, and the importer is set to: 
```testpkg.testmod```.

If we check the contents of testpkg/testmod.py, we cah see that indeed, the import is done there.
