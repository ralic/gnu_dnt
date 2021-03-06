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
import re

from   Debug      import *
from   Trace      import *
from   Command    import *
import Exceptions
import DB
import Tree
import Priority
import ID
import Root
import Entry
import Terminal
import Filter
import ANSI
import Text


def dump(filehandle,
         text,
         width,
         fill, wrap_fill,
         level) :
    debug("Building output")

    #
    # Build the output
    #
    debug("Wrapping entry text to " + str(width))

    # Remove trailing whitespaces (newlines will be added later)
    text = text.rstrip()

    # Dump each line
    dump = [ ]
    for i in text.split('\n') :
        if (width != 0) :
            w = width - (len(fill) * level)

            if (w <= 0) :
                dump = [ ]
                raise Exceptions.WidthTooSmall("cannot wrap " +
                                               "text "        +
                                               text)

            if (wrap_fill != "") :
                dump.extend(Text.wrap(i, w,
                                      subsequent_indent = wrap_fill,
                                      break_ansi_escapes = False))
            else :
                dump.extend(Text.wrap(i, w, break_ansi_escapes = False))
        else :
            dump.append(i)

    for j in dump :
        filehandle.write(fill * level + j + "\n")

def show_root(node,
              filehandle,
              width,
              level_fill, wrap_fill,
              level) :
    r = node

    debug("Visiting root entry " + str(r))

    text = r.text
    if (text != '') :
        dump(filehandle, text, width, level_fill, wrap_fill, level)
    else :
        debug("Empty output, skipping ...")

def show_entry(root_node,
               node,
               colors, verbose,
               cmap,
               filehandle,
               width,
               line_format, level_fill, wrap_fill,
               level) :
    e = node

    debug("Visiting entry " + str(e))

    text = e.text

    if (e.start != None) :
        start = e.start.tostring()
    else :
        start = "unknown"

    if (e.end != None) :
        end = e.end.tostring()
    else :
        end = "unknown"

    if (e.priority != None) :
        priority = e.priority.tostring()
    else :
        priority = "unknown"

    #
    # NOTE: 'done' get not substituted, yet ...
    #
    # if (e.done) :
    #    status = "complete"
    # else :
    #    status = "incomplete"

    if (e.comment != None) :
        comment = e.comment
    else :
        comment = ""

    depth = str(e.depth)

    id_temp = e.id
    id_absolute = str(id_temp)

    # Remove leading '0.' (we don't print anything related
    # to the Root node)
    id_absolute = re.sub('^0\.', '', id_absolute)

    try :
        id_list     = id_temp.tolist()
        id_relative = str(id_list[len(id_list) - 1])
    except :
        id_relative = "0"

    debug("Handling colors")

    # Handle colors
    if ((filehandle.isatty()) and (colors is True)) :
        color_info  = ANSI.normal_green
        color_index = ANSI.normal_green
        p           = e.priority.value
        try :
            color_text  = cmap[p]
        except KeyError :
            bug("Unknown key `" + p.tostring() + "'")
    else :
        # A bunch of pass-through lambdas
        color_text  = lambda x: x
        color_index = lambda x: x
        color_info  = lambda x: x
    assert(color_index != None)
    assert(color_text  != None)
    assert(color_info  != None)

    debug("Formatting")

    # Perform format substitutions
    t = line_format
    debug("input  = `" + t + "'")

    # NOTE:
    #   re.sub has the following "prototype":
    #
    #     re.sub(pattern, repl, string[, count])
    #
    # The optional argument count is the maximum
    # number of pattern occurrences to be replaced;
    # count must be a non-negative integer.
    # If omitted or zero, all occurrences will be
    # replaced.

    t = re.sub('%I', color_index(id_absolute),  t)
    t = re.sub('%i', color_index(id_relative),  t)
    t = re.sub('%s', start,                     t)
    t = re.sub('%e', end,                       t)
    t = re.sub('%p', color_text(priority),      t)
    t = re.sub('%c', comment,                   t)
    t = re.sub('%d', depth,                     t)
    t = re.sub('%r', root_node.text,            t)

    # Always substitute text at last in order to avoid re-substitutions
    # if text contains %i, %s, %e, %p, %c and so on

    # If line is set as "collapsed", substitute text with "..."
    assert('visible' in e.flags)
    if ('collapsed' in e.flags) :
        t = re.sub('%t', color_text('...'), t)
    else :
        t = re.sub('%t', color_text(text),  t)

    debug("output = `" + t + "'")

    if (t != '') :
        dump(filehandle, t, width, level_fill, wrap_fill, level)
    else :
        debug("Empty output, skipping ...")

def sort_children(children, sort_criteria) :
    m = None
    r = False

    debug("Sorting children")

    if (sort_criteria[len(sort_criteria) - 1] == "-") :
        r = True
        sort_criteria = sort_criteria[:len(sort_criteria) - 1]
        debug("  reverse sorting")

    if (sort_criteria == "id") :
        m = lambda x, y: cmp(x.id.tolist(), y.id.tolist())
    elif (sort_criteria == "priority") :
        m = lambda x, y: cmp(x.priority.toint(), y.priority.toint())
    elif (sort_criteria == "start") :
        m = lambda x, y: cmp(x.start.toint(), y.start.toint())
    elif (sort_criteria == "end") :
        m = lambda x, y : (1 if (x.end == None) else
                           (-1 if (y.end == None) else
                             cmp(x.end.toint(), y.end.toint())))
    else :
        bug("Unreachable!")

    debug("  sorting by " + sort_criteria)

    tmp = sorted(children, cmp = m, reverse = r)

    assert(tmp != None)

    return tmp

def show(root_node, node,
         colors, verbose,
         cmap,
         filehandle, width,
         line_format,
         indent_fill, unindent_fill, level_fill, wrap_fill,
         level,
         sort_criteria) :

    assert(root_node     != None)
    assert(node          != None)
    assert(isinstance(colors, bool))
    assert(isinstance(verbose, bool))
    assert(filehandle    != None)
    assert(width         >= 0)
    assert(indent_fill   != None)
    assert(line_format   != None)
    assert(unindent_fill != None)
    assert(level_fill    != None)
    assert(wrap_fill     != None)
    assert(level         >= 0)
    assert(sort_criteria != None)

    if (isinstance(node, Root.Root)) :

        if ('visible' in node.flags) :
            show_root(node,
                      filehandle,
                      width,
                      level_fill, wrap_fill,
                      level)
            level = level + 1

        # Updating root node
        if (root_node != node) :
            root_node = node
    elif (isinstance(node, Entry.Entry)) :

        if ('parent' in node.flags) :
            # XXX FIX ME:
            #     No decisions upon a parent node... Think about
            #     how we should handle them
            pass

        if ('visible'   in node.flags) :
            show_entry(root_node,
                       node,
                       colors, verbose,
                       cmap,
                       filehandle,
                       width,
                       line_format,
                       level_fill, wrap_fill,
                       level)
            level = level + 1

    else :
        bug("Unknown type " + str(type(node)))

    # Finally handle node children
    assert(hasattr(node, "children"))
    if (len(node.children) > 0) :

        children = node.children
        if (sort_criteria != "none") :
            children = sort_children(node.children,
                                     sort_criteria)

        if (('visible'   in node.flags) or
            ('collapsed' in node.flags) or
            ('parent'    in node.flags)) :

            if ('visible' in node.flags) :
                debug("Indenting more")
                filehandle.write(indent_fill)

            debug("Handling children")
            for j in children :
                show(root_node,
                     j,
                     colors, verbose,
                     cmap,
                     filehandle, width,
                     line_format,
                     indent_fill, unindent_fill, level_fill, wrap_fill,
                     level,
                     sort_criteria)

            if ('visible' in node.flags) :
                debug("Indenting less")
                filehandle.write(unindent_fill)

    else :
        debug("No children to handle")

def mark_ancestors(node,
                   show_root,
                   show_collapsed) :
    marked = 0
    parent = node.parent

    debug("Marking ancestors (show_collapsed = " + str(show_collapsed) + ")")

    while (parent != None) :
        debug("Entry `" +  str(parent)   +
              "' has marked as parent")
        parent.flags = [ 'parent' ]

        marked       = marked + 1
        node         = parent
        parent       = node.parent

    if (show_root is True) :
        debug("Entry `" +  str(node)   +
              "' has marked as visible")
        node.flags = [ 'visible', 'parent' ]

    return node, marked

def mark_children(node,
                  filter_obj,
                  show_root,
                  show_collapsed) :
    marked     = 0
    node.flags = []

    if (len(node.children) > 0) :
        debug("Marking " + str(len(node.children)) + " children")

        for i in node.children :
            m       = 0
            node, m = mark_children(i,
                                    filter_obj,
                                    show_root,
                                    show_collapsed)
            marked  = marked + m

        node = node.parent

    if (marked > 0) :
        debug("Entry `" +  str(node)   +
              "' has "  +  str(marked) +
              " children that match filter")

    if (isinstance(node, Root.Root)) :
        if (marked > 0) :
            debug("Entry `"                               + str(node)       +
                  "' has children those matches filter `" + str(filter_obj) +
                  "' marking it as collapsed")
            if (show_root is True) :
                node.flags = [ 'visible', 'collapsed' ]
            else :
                node.flags = ['collapsed']

    elif (isinstance(node, Entry.Entry)) :
        match = filter_obj.evaluate(node)

        if ((marked > 0) and (match is False)) :
            debug("Entry `"                               + str(node)       +
                  "' has children those matches filter `" + str(filter_obj) +
                  "' marking it as collapsed")
            if (show_collapsed is True) :
                node.flags = ['visible', 'collapsed']
            else :
                node.flags = ['collapsed']

        if (match is True) :
            debug("Entry `"            +  str(node)      +
                  "' matches filter `" + str(filter_obj) +
                  "', marking it as visible")
            node.flags = ['visible']
            marked     = marked + 1

    else :
        bug("Unknown type " + str(type(node)))

    return node, marked

def mark(node,
         filter_obj,
         show_root,
         show_collapsed) :
    assert(node != None)
    assert(filter != None)

    debug("Marking entries")

    # Marking all parent nodes up to root one because they belong to
    # the family and all children nodes those match the filter
    m       = 0
    node, m = mark_children(node, filter_obj, show_root, show_collapsed)
    debug("Found " + str(m) + " entries matching filters")

    m       = 0
    node, m = mark_ancestors(node, show_root, show_collapsed)
    debug("Found " + str(m) + " entries as ancestors")

    return node

class SubCommand(Command) :
    def __init__(self) :
        Command.__init__(self,
                         name   = "show",
                         footer = [
                "INDENT_FILL and UNINDENT_FILL are applied " + \
                    "when indentation is needed",
                "LINE_FORMAT controls the output for each entry " + \
                    "dumped.",
                "Interpreted sequences are:",
                "",
                "  %t  text",
                "  %s  start time",
                "  %e  end time",
                "  %p  priority",
                "  %I  index (absolute)",
                "  %i  index (relative)",
                "  %c  comment",
                "  %d  depth",
                "  %r  root node name",
                "",
                "FILTER         " + Filter.help_text(),
                "ID             " + ID.help_text(),
                "WIDTH          An integer >= 0, 0 means no formatting",
                "SORT_CRITERIA  Sorting output by id, start, end  or " + \
                    "priority (use '-' as suffix to reverse, eg. 'id-')"
                ])

    def short_help(self) :
        return "display node(s)"

    def authors(self) :
        return [ "Francesco Salvestrini" ]

    def do(self, configuration, arguments) :
        #
        # Parameters setup
        #
        Command.add_option(self,
                           "-o", "--output",
                           action = "store",
                           type   = "string",
                           dest   = "output",
                           help   = "specify output file name")
        Command.add_option(self,
                           "-i", "--id",
                           action = "store",
                           type   = "string",
                           dest   = "id",
                           help   = "specify starting node")

        Command.add_option(self,
                           "-l", "--line-format",
                           action = "store",
                           type   = "string",
                           dest   = "line_format",
                           help   = "specify line format")
        Command.add_option(self,
                           "-I", "--indent-fill",
                           action = "store",
                           type   = "string",
                           dest   = "indent_fill",
                           help   = "specify indent fill string")
        Command.add_option(self,
                           "-U", "--unindent-fill",
                           action = "store",
                           type   = "string",
                           dest   = "unindent_fill",
                           help   = "specify unindent fill string")
        Command.add_option(self,
                           "-L", "--level-fill",
                           action = "store",
                           type   = "string",
                           dest   = "level_fill",
                           help   = "specify level fill string")
        Command.add_option(self,
                           "-W", "--wrap-fill",
                           action = "store",
                           type   = "string",
                           dest   = "wrap_fill",
                           help   = "specify fill for wrapped lines")

        Command.add_option(self,
                           "-w", "--width",
                           action = "store",
                           type   = "string",
                           dest   = "width",
                           help   = "specify maximum text width")
        Command.add_option(self,
                           "-F", "--filter",
                           action = "store",
                           type   = "string",
                           dest   = "filter",
                           help   = "specify selection filter")
        Command.add_option(self,
                           "-C", "--hide-collapsed",
                           action = "store_false",
                           dest   = "show_collapsed",
                           help   = "hide collapsed entries")
        Command.add_option(self,
                           "-c", "--show-collapsed",
                           action = "store_true",
                           dest   = "show_collapsed",
                           help   = "show collapsed entries")
        Command.add_option(self,
                           "-R", "--hide-root",
                           action = "store_false",
                           dest   = "show_root",
                           help   = "hide root entries")
        Command.add_option(self,
                           "-r", "--show-root",
                           action = "store_true",
                           dest   = "show_root",
                           help   = "show root entries")

        Command.add_option(self,
                           "-s", "--sort",
                           action = "store",
                           type   = "string",
                           dest   = "sort_criteria",
                           help   = "sorting items")

        (opts, args) = Command.parse_args(self, arguments)
        if (len(args) > 0) :
            raise Exceptions.UnknownParameter(args[0])

        starting_id = opts.id
        if (starting_id == None) :
            starting_id = "0"
        node_id = ID.ID(starting_id)

        # Open output file
        filehandle = sys.stdout
        if (opts.output != None) :
            try :
                filehandle = open(opts.output, 'w')
            except :
                raise Exceptions.CannotWrite(opts.output)
        assert(filehandle != None)

        try :
            colors = configuration.get(PROGRAM_NAME, 'colors', bool)
        except :
            colors = False
        assert(isinstance(colors, bool))

        try :
            verbose = configuration.get(PROGRAM_NAME, 'verbose', bool)
        except :
            verbose = False
        assert(isinstance(verbose, bool))

        # Handling configuration
        width          = None
        show_collapsed = None
        show_root      = None
        line_format    = None
        level_fill     = None
        wrap_fill      = None
        unindent_fill  = None
        indent_fill    = None
        filter_text    = None
        sort_criteria  = None

        # Width
        if (opts.width != None) :
            try :
                width = int(opts.width)
            except :
                raise Exceptions.WrongParameterValue("width option must " +
                                                     "be an integer")
        else :
            # Try to guess terminal width
            t = Terminal.Terminal(stream_out = filehandle)
            w = t.columns
            assert(isinstance(w, int))

            # If width is not configured, used the guessed one
            width = configuration.get(self.name, 'width', int, w)
        assert(isinstance(width, int))

        # Width has to be >= 0 anyway ...
        if (width < 0) :
            raise Exceptions.WrongParameter("width must be greater "
                                            "or equal than 0")

        # Show collapsed
        if (opts.show_collapsed != None) :
            show_collapsed = opts.show_collapsed
        else :
            show_collapsed = configuration.get(self.name,
                                               'show_collapsed',
                                               bool,
                                               True)
        assert(isinstance(show_collapsed, bool))

        # Root entries
        if (opts.show_root != None) :
            show_root = opts.show_root
        else :
            show_root = configuration.get(self.name,
                                          'show_root',
                                          bool,
                                          False)
        assert(isinstance(show_root, bool))

        # Line format
        if (opts.line_format != None) :
            line_format = opts.line_format
        else :
            if (verbose is True) :
                l = "%i %t\n[%c]\n(%s, %e, %p)\n"
            else :
                l = "%i %t\n"

            line_format = configuration.get(self.name,
                                            'line_format',
                                            str,
                                            l)
        assert(isinstance(line_format, str))

        # Indent fill
        if (opts.indent_fill != None) :
            indent_fill = opts.indent_fill
        else :
            indent_fill = configuration.get(self.name,
                                            'indent_fill',
                                            str,
                                            "")
        assert(isinstance(indent_fill, str))

        # Unindent fill
        if (opts.unindent_fill != None) :
            unindent_fill = opts.unindent_fill
        else :
            unindent_fill = configuration.get(self.name,
                                              'unindent_fill',
                                              str,
                                              "")
        assert(isinstance(unindent_fill, str))

        # Level fill
        if (opts.level_fill != None) :
            level_fill = opts.level_fill
        else :
            level_fill = configuration.get(self.name,
                                           'level_fill',
                                           str,
                                           "    ")
        assert(isinstance(level_fill, str))

        # Level fill
        if (opts.wrap_fill != None) :
            wrap_fill = opts.wrap_fill
        else :
            wrap_fill = configuration.get(self.name,
                                          'wrap_fill',
                                          str,
                                          "")
        assert(isinstance(wrap_fill, str))

        # Filter text
        if (opts.filter != None) :
            filter_text = opts.filter
        else :
            filter_text = configuration.get(self.name,
                                            'filter',
                                            str,
                                            "not done")
        assert(isinstance(filter_text, str))

        # Sort method
        if (opts.sort_criteria != None) :
            sort_criteria = opts.sort_criteria.lower()
        else :
            sort_criteria = configuration.get(self.name,
                                              'sort_criteria',
                                              str,
                                              "id")
        assert(isinstance(sort_criteria, str))

        if (not sort_criteria in
            ["id"      , "id-",
             "start"   , "start-",
             "end"     , "end-",
             "priority", "priority-"]) :
            raise Exceptions.WrongParameterValue("option sort value "       +
                                                 "`" + sort_criteria + "' " +
                                                 "is unknown")

        # Use str() in order to avoid problems with None values
        debug("Configured values:")
        debug("  starting id    = `" + str(starting_id)     + "'")
        debug("  output         = `" + str(filehandle.name) + "'")
        debug("  width          = `" + str(width)           + "'")
        debug("  line format    = `" + str(line_format)     + "'")
        debug("  indent fill    = `" + str(indent_fill)     + "'")
        debug("  unindent fill  = `" + str(unindent_fill)   + "'")
        debug("  level fill     = `" + str(level_fill)      + "'")
        debug("  wrap fill      = `" + str(wrap_fill)       + "'")
        debug("  filter text    = `" + str(filter_text)     + "'")
        debug("  show_collapsed = `" + str(show_collapsed)  + "'")
        debug("  show_root      = `" + str(show_root)       + "'")
        debug("  sort criteria  = `" + str(sort_criteria)   + "'")

        # Build the filter
        filter_obj = Filter.Filter(filter_text)
        assert(filter_obj != None)

        #
        # Load database from file
        #
        db_file = configuration.get(PROGRAM_NAME, 'database', str)
        assert(db_file != None)
        db      = DB.Database()
        tree    = db.load(db_file)
        assert(tree != None)

        node = Tree.find(tree, node_id)
        if (node == None) :
            raise Exceptions.NodeUnavailable(str(node_id))

        #
        # Work
        #
        cmap = { Priority.PRIORITY_VERYHIGH : ANSI.bright_red,
                 Priority.PRIORITY_HIGH     : ANSI.bright_yellow,
                 Priority.PRIORITY_MEDIUM   : ANSI.bright_white,
                 Priority.PRIORITY_LOW      : ANSI.normal_cyan,
                 Priority.PRIORITY_VERYLOW  : ANSI.normal_blue }

        # mark() marks the filter-matching node children (1) and the nodes
        # up to the root (2)
        root = mark(node,
                    filter_obj,
                    show_root,
                    show_collapsed)

        # mark() returns the root node so show() descends through the
        # tree processing all nodes having collapsed, or parent or
        # visible (the others are skipped) flags printing the ones
        # those are marked as "visible"
        show(root,
             node,
             colors, verbose,
             cmap,
             filehandle, width,
             line_format,
             indent_fill, unindent_fill, level_fill, wrap_fill,
             0,
             sort_criteria)

        # Avoid closing precious filehandles
        if ((filehandle != sys.stdout) and (filehandle != sys.stderr)) :
            debug("Closing file `" + filehandle.name + "'")
            filehandle.close()

        debug("Success")


# Test
if (__name__ == '__main__') :
    debug("Test completed")
    sys.exit(0)
