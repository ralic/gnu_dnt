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
import datetime
import time

from   Debug import *
from   Trace import *

def today() :
    return datetime.date.today()

class Time(object) :
    since_epoch__ = 0

    def __init__(self, t = datetime.datetime.now()) :
        self.__since_epoch = time.mktime(t.timetuple())

    def __str__(self) :
        now = datetime.datetime.fromtimestamp(self.since_epoch__)
        return now.ctime()

    def fromstring(self, s) :
        self.since_epoch__ = int(s)

    def tostring(self) :
        debug("since-epoch = " + str(self.since_epoch__))
        return str(self.since_epoch__)

# Test
if (__name__ == '__main__') :
    t = Time()
    debug("Time is = " + str(t))
    debug("Test completed")
    sys.exit(0)
