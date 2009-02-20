#
# Copyright (C) 2008 Francesco Salvestrini
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys

from   Debug      import *
from   Trace      import *
import Exceptions
import Entry
import Root
import Tree

class Visitor(object) :
    def __init__(self, level_current = 0, index = 0, level_previous = 0) :
        self.__level_current  = level_current
        self.__level_previous = level_previous
        self.__index          = index
        debug("Visitor initialized")

# The following method must be provided by the subclass
#    def visitEntry(self, e) :
#        bug()

# The following method must be provided by the subclass
#    def visitRoot(self, r) :
#        bug()

    def level_previous(self) :
        return self.__level_previous

    def level_current(self) :
        return self.__level_current

    def index(self) :
        return self.__index

    def visit(self, n) :
        if (type(n) == Root.Root) :
            self.visitRoot(n)
        elif (type(n) == Entry.Entry) :
            self.visitEntry(n)
        else :
            bug("Unknown type " + str(type(n)) + " for Visitor")

        old_level            = self.__level_current
        self.__level_current = self.__level_current + 1
        index                = 0
        for j in n.children() :
            index        = index + 1
            self.__index = index
            # Please, re-accept myself ;-)
            j.accept(self)
        self.__level_current = old_level

# Test
if (__name__ == '__main__') :
    v = Visitor()

    class V(Visitor) :
        def __init__(self) :
            super(Visitor, self).__init__()

        def visitRoot(self, e) :
            pass

        def visitEntry(self, e) :
            pass

    debug("Test completed")
    sys.exit(0)
