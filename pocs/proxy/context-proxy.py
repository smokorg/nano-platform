def create_context_proxy(obj, handler):
    class _CTX_PROXY:
        def __getattribute__(self, attr_name):
            actual_attribute = None
            try:
                actual_attribute = obj.__getattribute__(attr_name)
            except AttributeError:
                pass
            return handler(obj, attr_name, actual_attribute)
            
    return _CTX_PROXY()


class TestClass:
    
    def __init__(self, carg):
        print('Constructor called with: %s' % carg)
        self.value = carg
    
    def get_value(self):
        print('get_value called')
        return self.value
    
    def set_value(self, value):
        print('set_value called with value=%s' % value)
        self.value = value

t = TestClass('one')
print('t=%s' % t)

def hnd(inst, attr_name, attr_value):
    print('Lookup for attribute: %s' % attr_name)
    print('Attribute in proxied instance: %s' % attr_value)
    if attr_value is None:
        print('Attribute is not found on proxied instance')
        raise AttributeError(attr_name)
    return attr_value

p = create_context_proxy(t, hnd)

v = p.get_value()
print('Value of v is: ' + v)
p.set_value('two')
v = p.get_value()
print('And now is: ' + v)
print('Calling non-existing method:')
try:
    p.non_exitent(1,2,'three')
except AttributeError as ae:
    print('Error: %s' % ae)

print('Referencing non exitent property:')
try:
    v = p.invalid
except AttributeError as ae:
    print('Error: %s' % ae)

