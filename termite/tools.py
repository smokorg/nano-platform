__author__ = 'pavle'


class Proxy:

    NATIVE_METHODS = ['target', '__method_call_wrapper__', 'on_method_call', 'on_property', 'on_missing' ,'__init__']

    def __init__(self, target):
        self.target = target

    def __getattribute__(self, name):
        if name in Proxy.NATIVE_METHODS:
            return super(Proxy, self).__getattribute__(name)
        try:
            attr = self.target.__getattribute__(name)
            try:
                getattr(attr, '__call__')
                return self.__method_call_wrapper__(name, self.on_method_call, attr)
            except ValueError:
                return self.on_property(name, attr)
        except ValueError:
            return self.on_missing(name)
    
    def __method_call_wrapper__(self, name, handler, actual_method):
        def method_wrapper(*args, **kwargs):
            return handler(name, actual_method, *args, **kwargs)
        return method_wrapper
    
    def on_method_call(self, name, actual_method, *args, **kwargs):
        return actual_method(*args, **kwargs)
    
    def on_property(self, name, prop_value):
        return prop_value
    
    def on_missing(self, name):
        return Proxy.__NOOP__property__()

    class __NOOP__property__:

        def __call__(self, *args, **kwargs):
            pass
