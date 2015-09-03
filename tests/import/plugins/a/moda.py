from modb import TestB

import logging


class ModuleAPlugin:

    def __init__(self):
        self.log = logging.getLogger('moda.ModuleAPlugin')
    
    def activate(self):
        self.log.info('Module A Plugin activated')
    
    def deactivate(self):
        self.log.info('Module A Plugin deactivated')

    def on_state_change(self, state):
        self.log.info('Module A Plugin state change: %s' % str(state))
