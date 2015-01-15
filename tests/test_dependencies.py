from logging import DEBUG
import logging
import sys
from unittest.case import TestCase
from nanopp.dependencies import DependenciesManager, Graph, Vertex

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


class TestGraph(TestCase):

    def test_find_circular_rings_1ring_3vertices(self):
        graph = Graph()
        a = graph.add_vertex(Vertex('A'))
        b = graph.add_vertex(Vertex('B'))
        c = graph.add_vertex(Vertex('C'))
        d = graph.add_vertex(Vertex('D'))

        graph.create_edge(a, b)
        graph.create_edge(b, c)
        graph.create_edge(c, a)
        graph.create_edge(c, d)

        rings = graph.find_circular_rings()
        self.assertTrue(len(rings) == 1)
        self.assertTrue([a, b, c], rings[0])

    def test_find_circular_rings_1ring_2vertices(self):
        graph = Graph()
        a = graph.add_vertex(Vertex('A'))
        b = graph.add_vertex(Vertex('B'))
        c = graph.add_vertex(Vertex('C'))

        graph.create_edge(a, b)
        graph.create_edge(b, a)
        graph.create_edge(b, c)

        rings = graph.find_circular_rings()
        self.assertTrue(len(rings) == 1)
        self.assertTrue([a, b], rings[0])

    def test_find_circular_rings_2rings_separate(self):
        graph = Graph()
        a = graph.add_vertex(Vertex('A'))
        b = graph.add_vertex(Vertex('B'))
        c = graph.add_vertex(Vertex('C'))
        d = graph.add_vertex(Vertex('D'))
        e = graph.add_vertex(Vertex('E'))
        f = graph.add_vertex(Vertex('F'))
        g = graph.add_vertex(Vertex('G'))

        graph.create_edge(a, b)
        graph.create_edge(b, c)
        graph.create_edge(c, a)
        graph.create_edge(a, d)
        graph.create_edge(e, d)
        graph.create_edge(e, g)
        graph.create_edge(g, f)
        graph.create_edge(f, e)

        rings = graph.find_circular_rings()
        self.assertTrue(len(rings) == 2)
        self.assertTrue([a, b, c], rings[0])
        self.assertTrue([e, g, f], rings[1])
