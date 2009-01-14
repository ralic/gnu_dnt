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

from   Debug         import *
from   Trace         import *
from   Command       import *
import Exceptions
import Color
import DB
import Priority
from   Root          import *
from   Entry         import *

class Visitor :
    def __init__(self, colors, be_verbose, show_all) :
        self.__colors  = colors
        self.__verbose = be_verbose
        self.__all     = show_all

        self.__indent  = ""
        self.__index   = 0
        self.__cmap    = {
            Priority.Priority.PRIORITY_VERYHIGH : bright_red,
            Priority.Priority.PRIORITY_HIGH     : bright_yellow,
            Priority.Priority.PRIORITY_MEDIUM   : bright_white,
            Priority.Priority.PRIORITY_LOW      : normal_cyan,
            Priority.Priority.PRIORITY_VERYLOW  : normal_blue,
            }

    def visitEntry(self, e) :
        assert(e != None)

        #debug("Visiting entry " + str(e))

        if (self.__colors) :
            color_info  = normal_green
            color_index = normal_green
            p           = e.priority.value()
            try :
                color_text  = self.__cmap[p]
            except KeyError :
                bug("Unknown key `" + p.tostring() + "'")
                color_text = white
        else :
            # A bunch of pass-through lambdas
            color_index = lambda x: x
            color_text  = lambda x: x
            color_info  = lambda x: x

        assert(color_index != None)
        assert(color_text != None)

        if (e.done()) :
            header = "-"
        else :
            header = " "

        if ((not e.done()) or (e.done() and self.__all)) :
            print(header                               +
                  self.__indent                        +
                  color_index(str(self.__index) + ".") +
                  color_text(e.text))
            if (self.__verbose) :
                l    = " " * (len(header) + len(str(self.__index)) + len("."))
                line1 = self.__indent + l

                line1 = line1 + color_info("Start:") + " "
                if (e.start != None) :
                    line1 = line1 + e.start.tostring()
                else :
                    line1 = line1 + "Unknown"
                line1 = line1 + " " + color_info("End:") + " "
                if (e.end != None) :
                    line1 = line1 + e.end.tostring()
                else :
                    line1 = line1 + "Unknown"

                line2 = self.__indent + l +         \
                    color_info("Priority:") + " " + \
                    e.priority.tostring() +         \
                    " " + color_info("Duration:") + " "
                if (e.end != None) :
                    d = e.end - e.start
                    line2 = line2 + d.tostring()
                else :
                    line2 = line2 + "Incomplete"

                print(line1)
                print(line2)
                print("")

    def visitRoot(self, r) :
        assert(r != None)

        #debug("Visiting root " + str(r))

        if (self.__colors) :
            color_index = normal_green
            color_text = normal_white
        else :
            color_index = lambda x: x # pass-through
            color_text  = lambda x: x # pass-through

            assert(color_index != None)
            assert(color_text != None)

        print(self.__indent                 +
              color_index(str(self.__index) + ".") +
              color_text(r.text))

    def visit(self, n) :
        if (type(n) == Root) :
            self.visitRoot(n)
        elif (type(n) == Entry) :
            self.visitEntry(n)
        else :
            bug()

        old_indent = self.__indent
        old_index  = self.__index

        self.__indent = self.__indent + "    "
        self.__index  = 0

        for j in n.children() :
            self.__index = self.__index + 1
            j.accept(self) # Re-accept myself

        self.__indent = old_indent
        self.__index  = old_index

class SubCommand(Command) :
    def __init__(self) :
        Command.__init__(self, "show")

    def short_help(self) :
        return "display node(s)"

    def authors(self) :
        return [ "Francesco Salvestrini" ]

    def do(self, configuration, arguments) :
        Command.add_option(self, "-a", "--all",
                           action = "store_true",
                           dest   = "all",
                           help   = "show all nodes")

        (opts, args) = Command.parse_args(self, arguments)

        # Parameters setup

        # Work

        # Load DB
        db_file = configuration.get(PROGRAM_NAME, 'database')
        assert(db_file != None)

        db   = DB.Database()
        tree = db.load(db_file)
        assert(tree != None)

        try :
            colors = configuration.get(PROGRAM_NAME, 'colors', raw = True)
        except :
            debug("No colors related configuration, default to false")
            colors = False
        try :
            verbose = configuration.get(PROGRAM_NAME, 'verbose', raw = True)
        except :
            debug("No verboseness related configuration, default to false")
            verbose = False

        show_all = False
        if (opts.all == True) :
            show_all = True

        v = Visitor(colors, verbose, show_all)
        tree.accept(v)

        debug("Success")

# Test
if (__name__ == '__main__') :
    debug("Test completed")
    sys.exit(0)
