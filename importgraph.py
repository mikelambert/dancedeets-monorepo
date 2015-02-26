#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Copyright (c) 2006 Guillaume Chazarain <guichaz@yahoo.fr>
#
# Intended usage:
#   o If you prefix your module names with the project names:
# $ cd my_python_project
# $ importgraph.py . | dot -Tpng -oimportgraph.png
#   o Otherwise:
# $ cd my_python_project/..
# $ importgraph.py my_python_project | dot -Tpng -oimportgraph.png
#
# History:
#  20061027: Initial release
#

import os
import sys
import optparse
import parser
import symbol
import token

def iter_over_ident(ast_tuple_node, ident):
    """Yield all tuples having ident as name in the ast"""
    if isinstance(ast_tuple_node, tuple):
        if ast_tuple_node[0] == ident:
            yield ast_tuple_node
        for node in ast_tuple_node:
            for stmt_tuple in iter_over_ident(node, ident):
                yield stmt_tuple

def get_dotted_names(import_stmt):
    """Extract the list of dotted names from the import statement tuple"""
    dotted_names = []
    for t in iter_over_ident(import_stmt, symbol.dotted_name):
        dotted_list = [name for nr, name in iter_over_ident(t, token.NAME)]
        dotted_names.append('.'.join(dotted_list))
    full_names = []
    for t in iter_over_ident(import_stmt, symbol.import_as_name):
        full_names.extend([prefix  + '.' + t[1][1] for prefix in dotted_names])
    full_names = full_names or dotted_names
    return full_names

def get_import_names(ast_tuple):
    """Get all imported names"""
    import_statements_iter = iter_over_ident(ast_tuple, symbol.import_stmt)
    res = []
    for import_stmt in import_statements_iter:
        res.extend(get_dotted_names(import_stmt))
    return res

def get_local_modules(ast_tuple):
    """Get imported python files, but only those residing in the project
    directory"""
    module_names = get_import_names(ast_tuple)
    res = []
    for mod in module_names:
        path = mod.replace('.', '/')
        attempts = [path + '.py', path]
        prefix = os.path.dirname(path)
        if prefix:
            attempts.extend([prefix + '.py', prefix])
        for attempt in attempts:
            if os.path.exists(attempt):
                res.append(attempt)
                break
    return list(set(res))

def clean_filename(filename):
    """A module name won't be prefixed by './' so a path should neither."""
    if filename.startswith('./'):
        filename = filename[2:]
    return filename

def print_import_graph(path):
    """Parse the file and produce a graph suitable to graphviz of the imported
    files present in the project directory"""
    print 'digraph G {'
    for root, dirs, files in os.walk(path):
        for file_basename in files:
            if file_basename.endswith('.py'):
                full_path = root + '/' + file_basename
                source_file = open(full_path)
                source_file_content = source_file.read()
                source_file.close()
                # parser.suite() does not like Windows line endings
                source_file_content = source_file_content.replace('\r', '')
                try:
                    ast = parser.suite(source_file_content)
                except SyntaxError, e:
                    print >> sys.stderr, \
                          'Syntax error parsing %s:' % (full_path), e
                    continue
                ast_tuple = ast.totuple()
                deps = get_local_modules(ast_tuple)
                for d in deps:
                    print '\t"%s" -> "%s"' % (clean_filename(full_path), d)
    print '}'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print_import_graph(sys.argv[1])
    else:
        print >> sys.stderr, 'Usage: %s DIRECTORY [| dot -Tpng -ograph.png]' % \
                             (sys.argv[0])
        sys.exit(1)
