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
from   Command    import *
import Exceptions
import ID
import DB
import Entry
import Tree
import Time
from   Visitor    import *

class NotDoneVisitor(Visitor) :
    def __init__(self, verbose) :
        super(NotDoneVisitor, self).__init__()
        self.__verbose = verbose

    def visitEntry(self, e) :
        assert(e != None)

        if (not e.done()) :
            e.mark_as_not_done()

    def visitRoot(self, r) :
        assert(r != None)

class SubCommand(Command) :
    def __init__(self) :
        Command.__init__(self,
                         name   = "not-done",
                         footer = [
                "ID  " + ID.help()
                ])

    def short_help(self) :
        return "mark node (and its children) as done"

    def authors(self) :
        return [ "Francesco Salvestrini" ]

    def do(self, configuration, arguments) :
        #
        # Parameters setup
        #
        Command.add_option(self,
                           "-i", "--id",
                           action = "store",
                           type   = "string",
                           dest   = "id",
                           help   = "specify node")

        (opts, args) = Command.parse_args(self, arguments)
        if (len(args) > 0) :
            raise Exceptions.UnknownParameter(args[0])

        if (opts.id == None) :
            raise Exceptions.MissingParameters("node id")

        id = ID.ID(opts.id)

        try :
            verbose = configuration.get(PROGRAM_NAME, 'verbose', raw = True)
        except :
            debug("No verboseness related configuration, default to false")
            verbose = False
        assert(verbose != None)

        #
        # Load database from file
        #
        db_file = configuration.get(PROGRAM_NAME, 'database')
        assert(db_file != None)
        db      = DB.Database()
        tree    = db.load(db_file)
        assert(tree != None)

        #
        # Work
        #
        node = Tree.find(tree, id)
        if (node == None) :
            raise Exceptions.NodeUnavailable(str(id))
        assert(node != None)

        # Mark node as not-done
        node.mark_as_not_done()

        # Mark node's children as not-done
        for i in node.children() :
            v = NotDoneVisitor(verbose)
            node.accept(v)

        #
        # Save database back to file
        #
        db.save(db_file, tree)

        debug("Success")

# Test
if (__name__ == '__main__') :
    debug("Test completed")
    sys.exit(0)