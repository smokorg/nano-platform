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