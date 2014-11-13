import tmod.test_pep302
print('Will try to import now...')
import sys
print(sys.meta_path)
tmod.test_pep302.perform_302_test()

import lajno
