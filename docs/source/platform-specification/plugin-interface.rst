Plugin Protocol
================

Termite platform manages the plugins as objects. Each registered plugin on the
platform is wrapped in a plugin container. This container manages the plugin
life-cycle and takes care to call the plugin hooks.

When you register a plugin, you tell termite which classes to instantiate as plugins.
This is the entry point for your plugin. Termite platform will examine your plugin
manifest and will try to instantiate the classes you've specified with "Plugin-Classes:".
But, you can also tell the platform to notify you for the life-cycle chnages of the
plugin. To do this, you need to expose hooks to the platform. This is easier than
it sounds. When writing the Plugin Classes for your plugin, you just need to follow
this protocol:

  class Plugin:
    def activate(self):
        pass

    def deactivate(self):
        pass

    def on_state_change(self, state):
        pass

Note that each of these methods is optional, i.e you can leave it out of from
your class.
The methods will be called if present in the resulting instance, in the following
condition:

 * ``activate(self)`` - called when the plugin is activated. This is the life-cycle
 state when the plugin has been fully initialized and is ready to be used. You
 can safely start whatever the plugin needs to do when this method is called.
 * ``deactivate(self)`` - called when the plugin is stopped, before being disposed.
 This means that the plugin life-cycle is near its end and you should clean up, close
 connections, flush, close resources so the plugin can complete normally.
 * ``on_state_change(self, state)`` - this is for finer control. This method is
 called whenever the plugin changes its state. The method has one argument - the
 new state. Note that this method will be called even if ``activate`` or
 ``deactivate`` have been called. You need to make sure you don't perform the
 same actions twice.

 As a conveninece, you can extend the class ``termite.platform.Plugin`` and override
 any of the above methods. Beside the protocol aboveve, this class also has the
 plugin states as static properties.
You can choose not to extend this class, and then you can write your own implementation -
the life-cycle of the plugin would be managed exactly the same.
