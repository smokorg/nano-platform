#    This file is part of Termite Plugins Platform
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

"""
    Python Wheels manipulation.
    Reference: https://www.python.org/dev/peps/pep-0427
    Ref. Impl: https://bitbucket.org/pypa/wheel
    
    This module provides abstraction on the wheel standard format.
    The aim is to manipulate python wheel packages as a single file (.whl) but 
    also as other structures (exploded .whl, zip, tar etc)
"""


