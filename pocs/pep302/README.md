PEP 302 Finder/Loader Proof-Of-Concept
--------------------------------------

__GOAL__

The POC will show that we can create Finder/Loader based on PEP-302(New Import Hooks)
that will:

 * Make appropriate distinctions between package/module and thus restricting the import of
 certain objects from a module.
 * Will be able to mark who is making the import, so we can have fine-grained control over
 the imported objects
 * Rewrite and replace the __import__ builtin and replace it in a specific submodule