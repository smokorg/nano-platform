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

"""Resources loading and management."""

import os


class BaseResourceLoader:
    """Base class for ResourceLoader implementors.
    
    A ResourceLoader is an object used to load some kind of resource. The 
    resource may be loaded from the system, from a file, fetched from a store or
    a caching mechanism, or by other means. The resource may be loaded as a 
    string, stream of bytes, a file or any other Python object (or may in fact 
    be a Python object itself).
    
    The ResourceLoader protocol defines only one method:
    
        class ResourceLoader:

            def load(self, str_rc_id_specs, *args, **kwargs):
                # perform the lookup and load here
    
    The ```load``` method delegates the loading of the actual resource to a 
    ProtocolHandler. The resource is loaded by its identifier. Optionally, an
    additional arguments may be passed to the ```load``` call which could 
    provide hints for the resource loading process.
    
    This base class delegates the actual loading of the resource to pre-defined
    ProtocolHandlers. One handler is registered per protocol. When the actual
    protocol path is resolved from the resource id a ProtocolHandler for the
    requested protocol is located. If such handler is registered, the resolved
    resource path along with any additional arguments are passed to the handler
    to load the actual resource.
    This class provides means to register protocol handlers and resolution of 
    resource id to a resource path and protocol.
    """
    def __init__(self, protocol_handlers=None):
        """Creates new ResouceLoader.
        
        A dictionary "protocol" => handler_instance may be provided when 
        initializing this object to be used as predefined protocol handlers.
        """
        protocol_handlers = protocol_handlers or {}
        self.protocol_handlers = {}
        
        for name, handler in protocol_handlers.items():
            self.add_handler(name, handler)
    
    def add_handler(self, protocol, handler):
        """Registers a ProtocolHandler for the given protocol with this resource
        loader.
        
        protocol is the protocol string (such as "http", "file", "zip").
        
        handler is the ProtocolHandler instance to be used when loading 
        resources using the specified protocol.
        """
        self.protocol_handlers[protocol] = handler
    
    def load(self, str_specs, *args, **kwargs):
        """Loads the resource identified by a resource id.
        
        The loading of the resources id done in two steps: first, the resource 
        id is resolved to a specific protocol and a resoruce path. Then a 
        protocol handler is looked up for the specific protocol and the loading
        of the resource is delegated to it by passing the resolved resource path
        along with any additional arguments.
        
        str_specs is the string representation of the resource id. The 
        specification for the resource id is defined like this:
            [[<protocol>:]...]<resource_id>
        where:
          * protocol is the protocol that determines the means of accessing 
          the resource (e.g. "file", "plugin", "class", etc).
          * resource_id is the actual resource ID. In the context of the access 
          mechanism (protocol handler), this may be: the file path, the name of 
          the plugin, the full class name, etc.
        
        Some examples of resource ids:     
          * plugin:core-event-loop
          * file:conf/platform.ini
          * class:nanopp.platform.Platform
          * singleton-object
          * bca87585-18bd-440f-87a9-7cc44e56a639
          
        or, some complex ones:
          * plugin:tar.gz:my-plugin-2.3
          * plugin:zip:ui-plugin.zip
          * file:zip:archive.zip/someFile.txt
        
        The method returns the loaded resource by the protocol handler.
        It throws an Exception if:
          * there is no registered handler for the actual prtoocol (the protocol
          is not supported)
          * any error occurs while actually loading the resource
        """
        protocol, path = self.get_path(str_specs)
        return self.get_handler(protocol).load(path, *args, **kwargs)
    
    def get_handler(self, protocol):
        """Looks up a ProtocolHandler instance for the specified protocol.
        
        If no such handler has been register, an Exception is raised.
        
        Returns the found protocol handler.
        """
        handler = self.protocol_handlers.get(protocol)
        if not handler:
            raise Exception('Protocol %s not supported' % protocol)
        return handler
    
    def get_path(self, str_specs):
        """Resolves the protocol and the resource path from the resource id spec
        string.
        
        str_spec is the resource id string. 
        
        The method returns a tupple (protocol, path) where the protocol may be 
        None.
        """
        protocol, sep, path = str_specs.partition(':')
        return protocol, path
    

class ProtocolHandler:

    def __init__(self, protocol, resource_loader):
        self.protocol = protocol
        self.resource_loader = resource_loader
    
    def load(self, path, *args, **kwargs):
        return None    


class FileProtocolHandler(ProtocolHandler):
    
    def __init__(self, resource_loader, base_path):
        self.base_path = base_path
        ProtocolHandler.__init__(self, 'file', resource_loader)
    
    def load(self, path, *args, **kwargs):
        path = self.get_real_path(path)
        rw = 'rw' in args or kwargs.get('rw')
        
        if self.valid_file(path):
            if 'as-string' in args or kwargs.get('as_string'):
                return self.load_file_as_text(path)
            else:
                return self.load_as_stream(path, rw)
    
    def load_file_as_text(self, path):
        with open(path) as fh:
            return fh.read()
    
    def load_as_stream(self, path, rw=False):
        mode = 'rw' if rw else 'r'
        fh = open(path, mode)
        return fh
    
    def get_real_path(self, path):
        return os.path.abspath("%s%s%s"%(self.base_path, os.path.sep, path))
    
    def valid_file(self, full_path):
        return os.path.exists(full_path) and os.path.isfile(full_path)
