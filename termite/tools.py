#    This file is part of Termite Plugins Platform
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
    Proxy type are available and will not be proxied (see the list of 
    NATIVE_METHODS).
    
    There are three extension points defined by the proxy that add facilities for
    interception of the interaction:
    
     - on_method_call - called every time a method is called and it exists in the 
        original object
     - on_property - called when a property is requested (to be read or written to)
     - on_missing - called when the actual method does not exist
    """

    NATIVE_METHODS = ['target', '__method_call_wrapper__', 'on_method_call', 'on_property', 'on_missing' ,'__init__']

    def __init__(self, target):
        """Creates new proxy object around the target object.
        
        target is the original object for which to create the Proxy.
        """
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
        """Creates a wrapper around the method call handler that curries the
        the method name and the actual method reference before the actual 
        arguments to the method invocation.
        """
        def method_wrapper(*args, **kwargs):
            return handler(name, actual_method, *args, **kwargs)
        return method_wrapper
    
    def on_method_call(self, name, actual_method, *args, **kwargs):
        """Called every time a method is called on the proxy and exists in the target.
        
        This is intended to be overriden in a subclass when extending. This method
        does not have to be implemented by any extending class. By default it
        will call the actual method from the proxied instance.
        
        name is the name of the called method.
        
        actual_method is an actual reference to the method from the underlying
        target method.
        
        args is a tupple of the arguments passed to the method call.
        
        kwargs is a dictionary of the arguments passed to the method call.
        
        By default returns the actual result of the method call. 
        """
        return actual_method(*args, **kwargs)
    
    def on_property(self, name, prop_value):
        """Called every time a property is requested and exists in the target.
        
        This method is intended to be implemented in an extending class. By
        default it will return the actual reference to the property of the 
        proxied instance.
        
        name is the name of the requested property.
        
        prop_value is the actual value (reference) of the property in the proxied
        object
        
        By default returns the actual value of the property in the proxied object.
        """
        return prop_value
    
    def on_missing(self, name):
        """Called when a request is being made to a non-existing property or method
        in the proxied object.
        
        Since it cannot be determined whether the request is for a property (to 
        get or set a value) or a method call, only the name of the requested 
        attribute is passed down to the call.
        
        name is the name of the property or method being requested.
        
        Returns a reference to a no-operation property. This is a callable instance
        that when called does not perform any operation (NOOP), but is not None.
        """
        return Proxy.__NOOP__property__()

    class __NOOP__property__:
        """No-operation callable.
        
        Defines a callable object that does not perform any operation.
        """
        def __call__(self, *args, **kwargs):
            """Performs no operation, just pass the execution.
            """
            pass
