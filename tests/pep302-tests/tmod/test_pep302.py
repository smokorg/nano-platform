
class TestImporter:
    def find_module(self, fullname, path=None):
        print(' [TestImporter]: find_module(%s, %s)'%(fullname, path))
        print('    => From: ',__name__)
    def load_module(self, fullname):
        pass


print('Executing')
import sys
sys.meta_path.insert(0, TestImporter())


def perform_302_test():

    # let's try importing now
    from tmod2.mod2 import test
    test()
if __name__=='__main__':
    perform_302_test()
