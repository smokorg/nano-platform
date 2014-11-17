PEP 302 Finder/Loader Proof-Of-Concept
--------------------------------------

POC Goals:

 * Import from a custom location, not in python path
 * Context-aware import - which module does the actual import
 * PEP-302 Finder
 * PEP-302 Loader
 * builtin function ```__import__`` can be replaced in the loaded modules, thus givig control over ```import`` and ```from-import``` statements
 * Restricting certain packages to be loaded
 * Restricting some modules to load certain packages
