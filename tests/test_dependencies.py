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
        dm.add_dependency('A', ['B', 'C'])
        dm.add_dependency('B', [])
        dm.add_dependency('C', ['D', 'E', 'F'])
        dm.add_dependency('D', ['F'])
        dm.add_dependency('E', ['B'])
        dm.add_dependency('F', ['E'])

        dependency_order = dm.get_install_order()
        self.assertEqual(['B', 'E', 'F', 'D', 'C', 'A'], dependency_order)