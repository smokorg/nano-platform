from logging import DEBUG
import logging
import sys
from unittest.case import TestCase
from termite.dependencies import DependenciesManager, Graph, Vertex, PluginDependenciesManager

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

    def test_find_circular_rings_2rings_mangled(self):
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
        graph.create_edge(c, d)
        graph.create_edge(d, e)
        graph.create_edge(e, a)
        graph.create_edge(e, f)
        graph.create_edge(e, g)
        graph.create_edge(f, d)

        rings = graph.find_circular_rings()
        self.assertTrue(len(rings) == 2)
        self.assertTrue([a, b, c, d, e], rings[0])
        self.assertTrue([d, e, f], rings[1])


class TestPluginDependenciesManager(TestCase):
    
    def test_dependency(self):
        pdm = PluginDependenciesManager()
        d = pdm.dependency('plugin.one')
        logging.info('Dependency: %s',d)
    
    def test_dependecy_reverese_order(self):
        pdm = PluginDependenciesManager()
        
        a = pdm.dependency('a')
        b = pdm.dependency('b')
        c = pdm.dependency('c')
        d = pdm.dependency('d')
        e = pdm.dependency('e')
        
        pdm.require('e','b', (0,False), (1,False))
        pdm.require('e','b', (1,False), (2,False))
        pdm.require('e','c', (0,False), (1,False))
        pdm.require('c','d', (0,False), (1,False))
        pdm.require('c','d', (1,False), (2,False))
        pdm.require('b','d', (0,False), (1,False))
        pdm.require('d','a', (0,False), (1,False))
        pdm.require('d','a', (1,False), (2,False))
        
        order = pdm.reverese_dependency_order()
        print('In order: %s' % str(order))
        
    def test_iterate_graph(self):
        pdm = PluginDependenciesManager()
        
        a = pdm.dependency('a')
        b = pdm.dependency('b')
        c = pdm.dependency('c')
        d = pdm.dependency('d')
        e = pdm.dependency('e')
        
        pdm.require('e','b', (0,False), (1,False))
        pdm.require('e','b', (1,False), (2,False))
        pdm.require('e','c', (0,False), (1,False))
        pdm.require('c','d', (0,False), (1,False))
        pdm.require('c','d', (1,False), (2,False))
        pdm.require('b','d', (0,False), (1,False))
        pdm.require('d','a', (0,False), (1,False))
        pdm.require('d','a', (1,False), (2,False))
        
        for d in pdm.dependencies_graph:
            logging.debug(d)
        
        
        
        
