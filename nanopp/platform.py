

class Plugin:
    """ Base class for all Plugins.
    
    This is the entry point in the plugin itself. Each plugin MUST exponse 
    at most one implementation of Plguin.
    
    """
    
    STATE_UNINSTALLED = 0x0
    """ The plugin is loaded but the installation has not yet taken place.
    """
    
    STATE_INSTALLED = 0x1
    """The plugin is installed on the platform.
    
    At this point all dependencis for the plugin had been resolved and satisfyed.
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
    def load_plugin(self, plugin_ref):
        pass

    def install(self):
        pass

    def resolve_dependencies(self):
        pass
    
    def activate(self):
        pass
        
    def deactivate(self):
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
