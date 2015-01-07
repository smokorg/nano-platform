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

__author__ = 'pavle'


class DependenciesManager:

    def __init__(self):
        self.dependencies = {}

    def add_dependency(self, dep_id, depends_on, ref=None):
        pass

    def build_dependency_graph(self):
        pass

    def get_dependency(self, dep_id):
        pass


class Vertex:

    def __init__(self, name):
        self.name = name
        self.edges = []

    def __str__(self):
        return "V(%s)" % self.name

    def __repr__(self):
        return self.__str__()


class Edge:

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.vertices = [head, tail]

    def __str__(self):
        return "E(%s - %s)" % (self.head.name, self.tail.name)

    def __repr__(self):
        return self.__str__()


class Graph:

    def __init__(self):
        self.vertices = []
        self.vertices_by_name = {}
        self.edges = []
        self.edges_by_vertex = {}

    def add_vertex(self, vertex):
        if self.vertices_by_name.get(vertex.name):
            raise Exception('Vertex %s already added' % vertex.name)
        self.vertices.append(vertex)
        self.vertices_by_name[vertex.name] = vertex
        return vertex

    def create_edge(self, head_vertex, tail_vertex):
        edge_id = self.__to_edge_id(head_vertex, tail_vertex)
        if not (self.vertices_by_name.get(head_vertex.name) and self.vertices_by_name.get(tail_vertex.name)):
            raise Exception("Edge to a vertex not known to this graph")
        if self.edges_by_vertex.get(edge_id):
            raise Exception("Edge (%s - %s) already exists" % (head_vertex, tail_vertex))
        edge = Edge(head=head_vertex, tail=tail_vertex)
        self.edges_by_vertex[edge_id] = edge
        self.edges.append(edge)
        return edge

    @staticmethod
    def __to_edge_id(head_v, tail_v):
        return "%s-%s" % (head_v.name, tail_v.name)

    def __str__(self):
        gs = "Graph: %d vertices, %d edges\n" % (len(self.vertices), len(self.edges))
        gs += "Vertices: %s\n" % self.vertices
        gs += "Edges: %s\n" % self.edges
        return gs

    def __repr__(self):
        return self.__str__()


class Dependency:

    def __init__(self, dep_name, depends_on=None, ref=None):
        self.name = dep_name
        self.dependencies = depends_on or []
        self.ref = ref
        self.dependants = []
        self.available = False

    def check_available(self):
        for dep in self.dependencies:
            if not dep.available:
                return False
        return True


if __name__ == '__main__':
    graph = Graph()

    a = graph.add_vertex(Vertex(name='A'))
    b = graph.add_vertex(Vertex(name='B'))
    c = graph.add_vertex(Vertex(name='C'))
    d = graph.add_vertex(Vertex(name='D'))
    e = graph.add_vertex(Vertex(name='E'))

    graph.create_edge(a, b)
    graph.create_edge(a, c)
    graph.create_edge(a, e)
    graph.create_edge(b, d)
    graph.create_edge(b, e)
    graph.create_edge(c, e)

    print(graph)


