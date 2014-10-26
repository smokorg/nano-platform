

class Plugin:
    STATE_UNINSTALLED = 0x0
    STATE_INSTALLED = 0x1
    STATE_ACTIVE = 0x2
    STATE_DEACTIVATED = 0x3
    STATE_DISPOSED = 0x4
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
