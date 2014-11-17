real_import = __import__

def test_import(*args, **kwargs):
    print('test import-ot')
    return real_import(*args, **kwargs)

__import__ = test_import    

import tmod.test_pep302
print('Will try to import now...')
import sys
print(sys.meta_path)
tmod.test_pep302.perform_302_test()
