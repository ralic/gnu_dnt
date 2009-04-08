#!/bin/sh

#
# gitlog-to-committers
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
# This program is based on gitlog-to-changelog by Jim Meyering
#

fmt='
        r=%(refname)
        t=%(*objecttype)
        T=${r#refs/tags/}

        o=%(*objectname)
        n=%(*authorname)
        e=%(*authoremail)
        s=%(*subject)
        d=%(*authordate)
        b=%(*body)

        if test "z$t" = z
        then
		# soft-tag
                t=%(objecttype)
                o=%(objectname)
                n=%(authorname)
                e=%(authoremail)
                s=%(subject)
                d=%(authordate:short)
                b=%(body)
        fi
	echo "$d $T"
'

eval=`git for-each-ref --shell --format="$fmt" \
    --sort=taggerdate \
    refs/tags`

eval "$eval"
