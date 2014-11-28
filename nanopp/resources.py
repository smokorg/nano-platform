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

import os

class BaseResourceLoader:
    def __init__(self, protocol_handlers={}):
        self.protocol_handlers = {}
        
        for name, handler in protocol_handlers.iteritems():
            self.add_handler(name, handler)
    
    def add_handler(self, protocol, handler):
        self.protocol_handlers[protocol] = handler
    
    def load(self, str_specs, *args, **kwargs):
        protocol, path = self.get_path(str_specs)
        return self.get_handler(protocol).load(path, *args, **kwargs)
    
    def get_handler(self, protocol):
        handler = self.protocol_handlers.get(protocol)
        if not handler:
            raise Exception('Protocol %s not supported' % protocol)
        return handler
    
    def get_path(self, str_specs):
        protocol, sep, path = str_specs.partition(':')
        return (protocol, path)
    

class ProtocolHanlder:

    def __init__(self, protocol):
        self.protocol = protocol
    
    def load(self, path, *args, **kwargs):
        return None    


class FileProtocolHandler(ProtocolHanlder):
    
    def __init__(self, base_path):
        self.base_path = base_path
        ProtocolHanlder.__init__(self, 'file')
    
    def load(self, path, *args, **kwargs):
        path = self.get_real_path(path)
        rw = 'rw' in args or kwargs.get('rw')
        
        if(self.valid_file(path)):
            if 'as-string' in args or kwargs.get('as_string'):
                return self.load_file_as_text(path)
            else
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
        
