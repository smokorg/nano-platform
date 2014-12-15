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
    
    At this point, the call to Plugin.activate(...) has been made and no error 
    were detected.
    """
    
    STATE_DEACTIVATED = 0x3
    """ The plugin has been deactivated, but it is still available on the platorm.
    """
    
    STATE_DISPOSED = 0x4
    """ The plugin is ready to be removed from the platform.
    
    This point may have been reached by calling PluginManager.dispose(...) or
    it may be a result of an error during installtion (such as dependencies that
    had not been satisfyed).
    
    The plugin will be completel removed from the platform on the next garbadge 
    collection cycle.
    """
    
    
    
    def activate(self):
        pass
    
    def deactivate(self):
        pass
    
    def on_state_change(self, state):
        pass
    


class PluginContainer:
    def load(self):
        pass

    def install(self):
        pass

    def resolve_dependencies(self):
        pass
    
    def activate(self):
        pass
        
    def deactivate(self):
        pass
    
    def uninstall(self):
        pass
    
    def dispose(self):
        pass
    

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
