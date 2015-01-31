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


import logging


class DependenciesManager:

    def __init__(self):
        self.dependencies = {}
        self.log = logging.getLogger('nanopp.dependencies.DependenciesManager')

    def add_dependency(self, dep_id, depends_on, ref=None):
        if self.dependencies.get(dep_id):
            raise Exception('Duplicate dependency definition. Dependency %s already added.' % dep_id)
        dep = self.create_dependency_instance(dep_id, depends_on, ref)
        self.dependencies[dep_id] = dep

        if depends_on:
            for dep_name in depends_on:
                existing_dep = self.dependencies.get(dep_name)
                if existing_dep:
                    existing_dep.dependants.append(dep)
        self.log.debug('Added dependency: %s => %s [ref=%s]' % (dep_id, depends_on, ref))

    def delete_dependency(self, dep_id):
        pass

    def create_dependency_instance(self, dep_id, depends_on, ref=None):
        dep = Dependency(dep_name=dep_id, depends_on=depends_on, ref=ref)
        return dep

    def build_dependency_graph(self):
        graph = Graph()
        edges = []
        for dep_id, dependency in self.dependencies.items():
            v = Vertex(dep_id)
            graph.add_vertex(v)
            for d in dependency.dependencies:
                edges.append((d, dep_id))

        for head, tail in edges:
            head_v = graph.get_vertex(head) or graph.add_vertex(Vertex(head))
            tail_v = graph.get_vertex(tail) or graph.add_vertex(Vertex(tail))

            graph.create_edge(tail_vertex=tail_v, head_vertex=head_v)

        return graph

    def get_dependency(self, dep_id):
        return self.dependencies.get(dep_id)

    def all_dependencies_satisfied(self, dep_id):
        dep = self.get_dependency(dep_id)
        if not dep:
            raise ValueError('Invalid dependency id: %s' % dep_id)
        if len(dep.dependencies) == 0:
            return True

        for d in dep.dependencies:
            if not d.available:
                return False
        return True

    def mark_available(self, dep_id):
        if self.all_dependencies_satisfied(dep_id):
            self.get_dependency(dep_id).available = True
            return True
        raise Exception('Not all dependencies available')

    def get_install_order(self):
        graph = self.build_dependency_graph()
        dependencies_order = []
        for vertex in graph.vertices:
            out_e = vertex.out_edges()
            # Locate a vertex that has no edges pointing outwards
            if not out_e or len(out_e) == 0:
                # start here
                sub_ordered_dependencies = self.__get_install_order_sub__(graph, vertex)
                dependencies_order = dependencies_order + sub_ordered_dependencies
        return [n.name for n in dependencies_order]

    def __get_install_order_sub__(self, graph, vertex):
        deps_in_order = []
        self.__traverse__(graph, vertex, deps_in_order)
        return deps_in_order

    @staticmethod
    def __count_unmarked_out_edges__(vertex):
        uoe_count = 0

        for edge in vertex.out_edges():
            if not edge.marked():
                uoe_count += 1

        return uoe_count

    def __traverse__(self, graph, vertex, dep_arr):
        if vertex.marked():
            return
        unm_oe_count = self.__count_unmarked_out_edges__(vertex)
        visit_vertices = []
        if unm_oe_count == 0:
            dep_arr.append(vertex)
            vertex.mark('added')
            for edge in vertex.in_edges():
                edge.mark('resolved')
                if not edge.tail.marked():
                    visit_vertices.append(edge.tail)

        for visit_vertex in visit_vertices:
            self.__traverse__(graph, visit_vertex, dep_arr)


class Markable:

    def __init__(self):
        self.__mark = None

    def mark(self, value):
        self.__mark = value

    def marked(self):
        return self.__mark


class Vertex(Markable):

    def __init__(self, name):
        self.name = name
        self.edges = []
        super().__init__()

    def __str__(self):
        return "V(%s)" % self.name

    def __repr__(self):
        return self.__str__()

    def add_edge(self, edge):
        self.edges.append(edge)

    def out_edges(self):
        oe = []
        for e in self.edges:
            if e.head is not self:
                oe.append(e)
        return oe

    def in_edges(self):
        ie = []
        for e in self.edges:
            if e.head is self:
                ie.append(e)
        return ie


class Edge(Markable):

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.vertices = [head, tail]
        super().__init__()

    def __str__(self):
        return "E(%s -> %s)" % (self.tail.name, self.head.name)

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

    def create_edge(self, tail_vertex, head_vertex):
        edge_id = self.__to_edge_id(head_vertex, tail_vertex)
        if not (self.vertices_by_name.get(head_vertex.name) and self.vertices_by_name.get(tail_vertex.name)):
            raise Exception("Edge to a vertex not known to this graph")
        if self.edges_by_vertex.get(edge_id):
            raise Exception("Edge (%s - %s) already exists" % (head_vertex, tail_vertex))
        edge = Edge(head=head_vertex, tail=tail_vertex)
        self.edges_by_vertex[edge_id] = edge
        self.edges.append(edge)
        head_vertex.add_edge(edge)
        tail_vertex.add_edge(edge)
        return edge

    def get_vertex(self, v_name):
        return self.vertices_by_name.get(v_name)

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

    class GraphIterator:

        def __init__(self, graph):
            self.graph = graph
            self.stack = []
            self.current_vertex = 0

        def __iter__(self):
            return self

        """
        DFS traversal:

        s = [] # stack
        for v in vertices:
            if not v.marked():
                s.append(n) # push to stack
                while len(s):
                    vx = s.pop()
                    if not vx.marked():
                        vx.mark('discovered')
                        yield vx
                    for edg in vx.out_edges():
                        if not edg.tail.marked():
                            s.append(edg.tail)
        """

        @staticmethod
        def __next_from_stack__(stack):
            vertex = stack.pop()
            if not vertex.marked():
                out_edges = vertex.out_edges()
                for edge in out_edges:
                    if not edge.head.marked():
                        stack.append(edge.head)
                vertex.mark('DISCOVERED')
                return vertex
            return None

        def __next__(self):
            if len(self.stack):
                vertex = None
                while vertex is None:
                    vertex = self.__next_from_stack__(self.stack)
                return vertex

            if self.current_vertex < len(self.graph.vertices):
                vertex = self.graph.vertices[self.current_vertex]
                while vertex.marked():
                    self.current_vertex += 1
                    if self.current_vertex < len(self.graph.vertices):
                        vertex = self.graph.vertices[self.current_vertex]
                    else:
                        raise StopIteration
                if vertex.marked():
                    raise StopIteration
                self.stack.append(vertex)
                return self.__next__()

            raise StopIteration()

    # Graph iterator - DFS traversal
    def __iter__(self):
        return Graph.GraphIterator(self.__clone__())

    def __clone__(self):
        return self

    def find_circular_rings(self):
        rings = []
        graph = self.__clone__()
        for vertex in graph.vertices:
            self.__traverse_cr__(vertex, [], {}, rings)
        return rings

    def __traverse_cr__(self, vertex, backtrack, visited, rings):
        if vertex.marked():
            return
        vertex.mark('visited')
        backtrack.append(vertex)
        visited[vertex.name] = vertex
        for edge in vertex.out_edges():
            if visited.get(edge.head.name):
                # cycle detected
                ring = []
                i = 0
                for v in backtrack:
                    if v == edge.head:
                        ring = backtrack[i:]
                        break
                    i += 1
                rings.append(ring)
            if not edge.head.marked():
                self.__traverse_cr__(edge.head, backtrack, visited, rings)

    def is_circular(self):
        return len(self.find_circular_rings()) > 0


class Dependency:

    def __init__(self, dep_name, depends_on=None, ref=None):
        self.name = dep_name
        self.dependencies = depends_on or []
        self.ref = ref
        self.dependants = []
        self.available = False
        
        if not len(self.dependencies):
            self.available = True

    def check_available(self):
        for dep in self.dependencies:
            if not dep.available:
                return False
        return True


class ServiceDependency(Dependency):

    def __init__(self, service_name, depends_on, factory=None):
        super(ServiceDependency, self).__init__(dep_name=service_name, depends_on=depends_on)
        self.factory = factory

    def make_available(self):
        if not (self.ref or self.factory):
            raise Exception('Service instance nor the factory method defined')
        if not self.ref:
            self.ref = self.make_service_instance()

    def make_service_instance(self):
        if not self.factory:
            raise Exception('Factory method not defined for this service: %s' % self.name)
        args = self.get_dependencies()
        return self.factory(*args)

    def get_dependencies(self):
        return [d.ref for d in self.dependencies]


class ServiceContext:
    
    def __init__(self):
        self.services = {}
        self.avail_listeners = {}
        self.remove_listeners = {}
    
    def __create_service_dependency__(self, srvc_name, dependencies, factory):
        deps = []
        srvc_dependency = self.__get_service_dep__(srvc_name, factory)

        for dep in dependencies:
            sd = self.__get_service_dep__(dep)
            deps.append(sd)
            if srvc_dependency not in sd.dependants:
                sd.dependants.append(srvc_dependency)
        srvc_dependency.dependencies = dependencies
        return srvc_dependency

    def __get_service_dep__(self, name, factory=None):
        dep = self.services.get(name)
        if not dep:
            dep = ServiceDependency(service_name=name, depends_on=[], factory=factory)
            self.services[name] = dep
        if not dep.factory:
            dep.factory = factory
        return dep

    def service(self, name, dependencies, factory):
        srv_dep = self.__create_service_dependency__(name, dependencies, factory)
        if not self.services.get(name):
            self.services[name] = srv_dep
        self.__check_available__(srv_dep)

    def __triger_available__(self, name, instance):
        pass

    def __triger_removed__(self, name, instance):
        pass

    def __check_available__(self, srv_dep):
        all_available = True
        for dep in srv_dep.dependencies:
            if not dep.available:
                all_available = False
                break
        if all_available:
            # notify the listeners
            # create the service itself
            srv_dep.make_service_instance()
            self.__triger_available__(srv_dep.name, srv_dep.ref)

            # notify dependants
            for dpd in srv_dep.dependants:
                self.__check_available__(dpd)
    
    def locate_service(self, name, on_available, on_removed):
        svc_dep = self.services.get(name)
        if svc_dep:
            if svc_dep.available:
                # call immediate
                pass
            else:
                # register for later
                pass
            # register on_remove
        else:
            pass
    
    def locate_services(self, services, on_all_available, on_removed, on_all_removed):
        pass
    
    def remove_service(self, name):
        pass
     


if __name__ == '__main__':
    graph = Graph()

    a = graph.add_vertex(Vertex(name='A'))
    b = graph.add_vertex(Vertex(name='B'))
    c = graph.add_vertex(Vertex(name='C'))
    d = graph.add_vertex(Vertex(name='D'))
    e = graph.add_vertex(Vertex(name='E'))
    f = graph.add_vertex(Vertex(name='F'))

    graph.create_edge(a, b)
    graph.create_edge(a, e)
    graph.create_edge(a, d)
    graph.create_edge(b, e)
    graph.create_edge(c, e)
    graph.create_edge(c, f)
    graph.create_edge(c, d)
    graph.create_edge(f, d)
    graph.create_edge(d, e)

    print(graph)

    for v in graph:
        print(v)
