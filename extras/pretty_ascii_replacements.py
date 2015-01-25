#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-25
#

"""
Reformat `workflow.search.ASCII_REPLACEMENTS` to make the source code
prettier.
"""

from __future__ import print_function, unicode_literals, absolute_import

import unicodedata

from workflow.search import ASCII_REPLACEMENTS

WIDTH = 70


def quote(s):
    if "'" in s:
        return '"{0}"'.format(s)
    else:
        return "'{0}'".format(s)

output = {}

for k in ASCII_REPLACEMENTS:
    v = ASCII_REPLACEMENTS[k]
    k = unicodedata.normalize('NFC', k)
    k = k.encode('unicode-escape')
    output[k] = v.encode('us-ascii')

rows = []
row = ''
for k, v in ASCII_REPLACEMENTS.items():
    lhs = "'{0}': ".format(k.encode('unicode-escape'))
    rhs = quote(v)
    if False:
        output = "{0}{1},".format(lhs.ljust(10), rhs.rjust(6))
    else:
        output = "{0}{1},".format(lhs, rhs)
    i = len(output)
    j = i + len(row)
    if j > WIDTH - 4:
        rows.append(row)
        row = ''
    row += ' {0}'.format(output)

if row:
    rows.append(row)

print('{')
for row in rows:
    print('    ' + row.strip())
print('}')
