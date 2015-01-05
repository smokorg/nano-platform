__author__ = 'pavle'

class Proxy:

    def __init__(self, target):
        self.target = target

    def __call__(self, *args, **kwargs):
        pass
