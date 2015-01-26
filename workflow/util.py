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

from contextlib import contextmanager
import os
import sys
import unicodedata


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

    filename = decode(filename)
    dirpath = decode(os.path.abspath(start_dirpath))
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


def decode(text, encoding='utf-8', normalization='NFC'):
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

    dirpath = decode(dirpath)

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


@contextmanager
def syspath(paths):
    """Temporarily adds ``paths`` to front of :data:`sys.path`"""
    _syspath = sys.path[:]
    for path in paths:
        sys.path.insert(0, path)
    yield
    sys.path = _syspath


####################################################################
# Helpers from blinker
# https://github.com/jek/blinker/
####################################################################

class _symbol(object):

    def __init__(self, name):
        """Construct a new named symbol."""
        self.__name__ = self.name = name

    def __repr__(self):
        return self.name

    # def __str__(self):
    #     return self.name

    # def __unicode__(self):
    #     return unicode(self.name, 'utf-8')

_symbol.__name__ = b'symbol'


class symbol(object):
    """A constant symbol.

    Is a singleton.

    """

    symbols = {}

    def __new__(cls, name):
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        try:
            return cls.symbols[name]
        except KeyError:
            return cls.symbols.setdefault(name, _symbol(name))
