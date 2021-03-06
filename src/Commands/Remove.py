# -*- python -*-

#
# Copyright (C) 2008, 2009 Francesco Salvestrini
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

from   Debug         import *
from   Trace         import *
from   Command       import *
import Exceptions
import DB
import ID
import Tree

class SubCommand(Command) :
    def __init__(self) :
        Command.__init__(self,
                         name   = "remove",
                         footer = [
                "ID  " + ID.help_text()
                ])

    def short_help(self) :
        return "remove node(s)"

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
                           help   = "specify node id to remove")
        Command.add_option(self,
                           "-r", "--recursive",
                           action = "store_true",
                           dest   = "recursive",
                           help   = "remove node and its children recursively")

        (opts, args) = Command.parse_args(self, arguments)
        if (len(args) > 0) :
            raise Exceptions.UnknownParameter(args[0])

        if (opts.id == None) :
            raise Exceptions.MissingParameters("node id")

        node_id = ID.ID(opts.id)

        debug("Removing node:")
        debug("  id = " + str(node_id))

        #
        # Load database from file
        #
        db_file = configuration.get(PROGRAM_NAME, 'database', str)
        assert(db_file != None)
        db      = DB.Database()
        tree    = db.load(db_file)
        assert(tree != None)

        #
        # Work
        #
        debug("Looking for node `" + str(node_id) + "'")
        node = Tree.find(tree, node_id)
        if (node == None) :
            raise Exceptions.WrongParameter("unknown node " +
                                            "`" + str(node_id) + "'")

        parent = node.parent
        if (parent == None) :
            raise Exceptions.WrongParameter("cannot remove root node")

        debug("Node "
              "`" + str(node_id) + "' "
              "has " + str(len(node.children)) + " child/children")

        if ((len(node.children) > 0) and (opts.recursive is not True)) :
            raise Exceptions.MissingParameters("--recursive")

        parent.remove(node)

        #tree.dump("")

        #
        # Save database back to file
        #
        db.save(db_file, tree)

        debug("Success")

# Test
if (__name__ == '__main__') :
    debug("Test completed")
    sys.exit(0)
