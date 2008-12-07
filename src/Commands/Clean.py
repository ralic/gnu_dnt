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

def description() :
    return "remove the database"

def do(configuration, arguments) :
    command = Command("remove")

    (opts, args) = command.parse_args(arguments)

    # Parameters setup
    db_file = configuration.get(PROGRAM_NAME, 'database')
    assert(db_file != None)

    # Work
    try :
	os.stat(db_file)
    except OSError, e:
	warning("Nothing to do, directory already clean")
	return 0
    except :
	bug()

    try :
	os.unlink(db_file)
    except IOError, e:
	error("Cannot clean the directory")
	return 1
    except :
	bug()

    return 0

# Test
if (__name__ == '__main__') :
    debug("Test completed")
    sys.exit(0)