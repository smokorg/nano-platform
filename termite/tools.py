__author__ = 'pavle'


class Proxy:
    """Proxy wrapper that adds facilities for intercepting inerations.
    
    Wraps the original (target) object and exposes its methods and properties as
    its own. This is achieved by overriding the __getattribute__ native method.
    When a property is requested (reading/setting a value to a property, calling a
    method) on the proxy object, the wrapped object is inspected and a convinient
    wrapper is returned back to the requestor.
    For the requesting party, the proxy object follows the same interface as the 
    original object type. Some special methods that belong specifically to the 
    Proxy type are black-listed and will not be returned if requested.
    
    There are three extension points defined by the proxy that add facilities for
    interception of the interaction:
    
     - on_method_call - called every time a method is called and it exists in the 
        original object
     - on_property - called when a property is requested (to be read or written to)
     - on_missing - called when the actual method does not exist
    """

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
