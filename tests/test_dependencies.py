from logging import DEBUG
import logging
import sys
from unittest.case import TestCase
from nanopp.dependencies import DependenciesManager

__author__ = 'pavle'

sys.path.append("../..")
logging.basicConfig(level=DEBUG)


class TestDependencyManager(TestCase):

    def test_create_dependency_graph(self):
        dm = DependenciesManager()
        dm.add_dependency('A', ['B', 'E', 'D'])
        dm.add_dependency('B', ['E'])
        dm.add_dependency('C', ['D', 'E', 'F'])
        dm.add_dependency('D', ['E'])
        dm.add_dependency('E', [])
        dm.add_dependency('F', ['D'])

        print(dm.build_dependency_graph())
        print(dm.get_install_order())