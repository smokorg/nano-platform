__author__ = 'pavle'


import logging


class EventsPlugin:

    def __init__(self):
        self.log = logging.getLogger('core.events.EventsPlugin')
    
    def activate(self):
        self.log.info('Core.Events Plgin activated')
    
    def deactivate(self):
        self.log.info('Core.Events Plgin deactivated')

    def on_state_change(self, state):
        self.log.info('Core.Evenets state change: %s' % str(state))
