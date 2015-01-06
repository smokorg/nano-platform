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
import logging
from nanopp.tools import Proxy


class Plugin:
    """ Base class for all Plugins.
    
    This is the entry point in the plugin itself. Each plugin MUST expose
    at least one implementation of Plguin.
    
    """
    
    STATE_UNINSTALLED = 0x0
    """ The plugin is loaded but the installation has not yet taken place or
    it has been uninstalled.
    """
    
    STATE_INSTALLED = 0x1
    """The plugin is installed on the platform.
    
    At this point all dependencies for the plugin had been resolved and satisfied.
    """
    
    STATE_ACTIVE = 0x2
    """ The plugin has been successfully activated.
    
    At this point, the call to Plugin.activate(...) has been made and no errors 
    were detected.
    """
    
    STATE_DEACTIVATED = 0x3
    """ The plugin has been deactivated, but it is still available on the platform.
    """
    
    STATE_DISPOSED = 0x4
    """ The plugin is ready to be removed from the platform.
    
    This point may have been reached by calling PluginManager.dispose(...) or
    it may be a result of an error during installation (such as dependencies that
    had not been satisfied).
    
    The plugin will be completely removed from the platform on the next garbage
    collection cycle.
    """

    def activate(self):
        pass
    
    def deactivate(self):
        pass
    
    def on_state_change(self, state):
        pass


class PluginContainer:

    def __init__(self, plugin_ref, resource_loader):
        self.loader = resource_loader
        self.plugin_ref = plugin_ref
        self.dependencies = []
        self.plugin_hooks = []
        self.plugin_state = None
        self.plugin = None
        self.logger = logging.getLogger('nanopp.platform.PluginContainer')
    
    def load(self):
        self.plugin = self.loader.load('plugin:' + self.plugin_ref)
        self.plugin_state = Plugin.STATE_UNINSTALLED

    def install(self):
        if self.plugin_state is not Plugin.STATE_UNINSTALLED:
            raise PluginLifecycleException("Cannot install plugin. Invalid state: %s" % str(self.plugin_state))
        try:
            self.resolve_dependencies()
            self.create_hooks()
            self.plugin_state = Plugin.STATE_INSTALLED
            self.notify_state_change(Plugin.STATE_INSTALLED)
        except Exception as e:
            self.plugin_state = Plugin.STATE_DISPOSED
            raise e

    def create_hooks(self):
        manifest = self.plugin.get_manifest()
        for hook_class_name in manifest.plugin_classes:
            hook_class = self.loader.load('class:'+hook_class_name)
            hook_inst = hook_class()
            if not isinstance(hook_inst, Plugin):
                hook_inst = Proxy(target=hook_inst)
            self.plugin_hooks.append(hook_inst)

    def resolve_dependencies(self):
        pass
    
    def activate(self):
        if self.plugin_state is not Plugin.STATE_INSTALLED or self.plugin_state is not  Plugin.STATE_DEACTIVATED:
            raise PluginLifecycleException("Cannot activate plugin. Invalid state: %s" % str(self.plugin_state))
        try:
            for hook in self.plugin_hooks:
                hook.activate()
            self.plugin_state = Plugin.STATE_ACTIVE
            self.notify_state_change(Plugin.STATE_ACTIVE)
        except Exception as e:
                self.logger.error("Activation error in hook: %s. Error: %s" % (hook, e))
                self.plugin_state = Plugin.STATE_DEACTIVATED
                self.notify_state_change(Plugin.STATE_DEACTIVATED)

    def deactivate(self):
        pass
    
    def uninstall(self):
        pass
    
    def dispose(self):
        pass

    def notify_state_change(self, state):
        for hook in self.plugin_hooks:
            try:
                hook.on_state_chnage(state)
            except Exception as e:
                self.logger.error('Error on state change in hook: %s. Error: %s', hook, e)
    

class Platform:
    def start(self):
        pass
    
    def shutdown(self):
        pass


class PluginManager:
    def install_plugin(self, plugin_ref):
        pass

    def activate_plugin(self, plugin_id):
        pass
    
    def deactivate_plugin(self, plugin_id):
        pass
        
    def uninstall_plugin(self, plugin_id):
        pass
        
    def gc(self):
        pass


class PlatformException(Exception):
    pass


class PluginLifecycleException(PlatformException):
    pass