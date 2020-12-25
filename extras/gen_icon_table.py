#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-07
#

"""

Generate a ReST table of icons in :mod:`workflow.workflow` with previews.

"""



import os
import subprocess
import workflow

outdir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                      'docs', '_static')


def make_thumbnail(infile, outfile):
    cmd = ['sips', '-Z', '64', '-s', 'format', 'png', infile, '--out', outfile]
    # print(cmd)
    subprocess.call(cmd)


entries = []

col1 = col2 = 0

for name in dir(workflow):
    if name.startswith('ICON_'):
        const = getattr(workflow, name)
        # print('{} : {}'.format(name, const))
        filename = '{}.png'.format(name)
        make_thumbnail(const, os.path.join(outdir, filename))
        image = '.. image:: ../_static/{}'.format(filename)
        entries.append((name, image))
        if len(name) > col1:
            col1 = len(name)
        if len(image) > col2:
            col2 = len(image)

col1 += 5


print(('+' + ('-' * col1) + '+' + ('-' * col2) + '+'))
print(('| Name'.ljust(col1 + 1) + '| Preview'.ljust(col2 + 1) + '|'))
print(('+' + ('=' * col1) + '+' + ('=' * col2) + '+'))
for name, image in entries:
    print(('|``{}``'.format(name).ljust(col1 + 1) + '|' +
          image.ljust(col2) + '|'))
    print(('+' + ('-' * col1) + '+' + ('-' * col2) + '+'))

