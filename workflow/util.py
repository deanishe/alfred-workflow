#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-24
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import unicodedata

from workflow.base import get_logger

log = get_logger(__name__)


def find_upwards(filename, start_dirpath=None):
    """Search up directory tree for ``filename``

    If ``start_dirpath`` is not specified, current working
    directory will be used.

    :param filename: Name of file to search for
    :param start_dirpath: Directory to start searching
    :returns: path to first matching file or ``None``

    """

    if start_dirpath is None:
        start_dirpath = os.getcwdu()

    dirpath = os.path.abspath(start_dirpath)
    result = None

    while True:
        path = os.path.join(dirpath, filename)
        if os.path.exists(path):
            result = path
            break
        elif dirpath == '/':
            # reached top, nothing found
            break

        # move up to parent directory
        dirpath = os.path.dirname(dirpath)

    return result


def decode(self, text, encoding='utf-8', normalization='NFC'):
    """Return ``text`` as normalised unicode.

    If ``encoding`` and/or ``normalization`` is ``None``, the
    ``input_encoding``and ``normalization`` parameters passed to
    :class:`Workflow` are used.

    :param text: string
    :type text: encoded or Unicode string. If ``text`` is already a
        Unicode string, it will only be normalised.
    :param encoding: The text encoding to use to decode ``text`` to
        Unicode.
    :type encoding: ``unicode``
    :param normalization: The nomalisation form to apply to ``text``.
    :type normalization: ``unicode``
    :returns: decoded and normalised ``unicode``

    """

    if not isinstance(text, unicode):
        text = unicode(text, encoding)
    return unicodedata.normalize(normalization, text)


def create_directory(dirpath):
    """Create directory ``dirpath`` if it doesn't exist

    :param dirpath: path to directory
    :type dirpath: ``unicode``
    :returns: ``dirpath``
    :rtype: ``unicode``

    """

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath
