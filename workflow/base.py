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
Common core workflow functions, such as exceptions, constants and
logging.

"""

from __future__ import print_function, unicode_literals, absolute_import

import logging
import logging.handlers
import os
import re

from .util import symbol


try:
    from logging import NullHandler
except ImportError:  # pragma: no cover
    class NullHandler(logging.Handler):
        def emit(self, *args, **kwargs):
            pass


####################################################################
# Constants
####################################################################

#: Sentinel for properties that haven't been set yet (that might
#: correctly have the value ``None``)
UNSET = symbol('UNSET')


# Key names for library's saved settings.
# These can't be symbols, as they get serialised to JSON
# ------------------------------------------------------------------

#: User override for diacritic folding. Set with ``foldingon``,
#: ``foldingoff`` & ``foldingdefault`` :ref:`magic-arguments`.
KEY_DIACRITICS = '__aw_diacritic_folding'
#: User override for automatic update checks. Set with
#: ``autoupdateon`` and ``autoupdateoff`` :ref:`magic-arguments`.
KEY_AUTO_UPDATE = '__aw_autoupdate'
#: :mod:`~workflow.background` process name for the updater script.
KEY_UPDATER = '__aw_background_updater'
#: :mod:`~workflow.background` process name for the installer script.
KEY_INSTALLER = '__aw_background_installer'
#: Cache key update data is stored under.
KEY_UPDATE_DATA = '__aw_update_data'
#: Settings key last version run is saved under.
KEY_VERSION_LAST_RUN = '__aw_last_version_run'


####################################################################
# Keychain access errors
####################################################################

class KeychainError(Exception):
    """Raised by methods :meth:`Workflow.save_password`,
    :meth:`Workflow.get_password` and :meth:`Workflow.delete_password`
    when ``security`` CLI app returns an unknown error code.

    """


class PasswordNotFound(KeychainError):
    """Raised by method :meth:`Workflow.get_password` when ``account``
    is unknown to the Keychain.

    """


class PasswordExists(KeychainError):
    """Raised when trying to overwrite an existing account password.

    You should never receive this error: it is used internally
    by the :meth:`Workflow.save_password` method to know if it needs
    to delete the old password first (a Keychain implementation detail).

    """


####################################################################
# Data models
####################################################################

class Version(object):
    """Mostly semantic versioning

    The main difference to proper :ref:`semantic versioning <semver>`
    is that this implementation doesn't require a minor or patch
    version.

    >>> v1 = Version('2.5')
    >>> v2 = Version('2.5.1')
    >>> v1 > v2
    False
    >>> v1 == v2
    False
    >>> v1 < v2
    True
    >>> v3 = Version('2.5-beta')
    >>> v1 > v3  # release > beta
    True
    >>> v4 = Version('v2.5')
    >>> v1 == v4
    True
    >>> v = Version('dave')
    Traceback (most recent call last):
        ...
    ValueError: Invalid version number: dave
    >>> v = Version('1.1.1.1')
    Traceback (most recent call last):
        ...
    ValueError: Invalid version (too long): 1.1.1.1
    >>> v = Version('1.1.1alpha')
    Traceback (most recent call last):
        ...
    ValueError: Invalid suffix: `alpha`. Must start with `-`
    """

    #: Match version and pre-release/build information in version strings
    match_version = re.compile(r'([0-9\.]+)(.+)?').match

    def __init__(self, vstr):
        self.vstr = vstr
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.suffix = ''
        self.build = ''
        self._parse(vstr)

    def _parse(self, vstr):
        if vstr.startswith('v'):
            m = self.match_version(vstr[1:])
        else:
            m = self.match_version(vstr)
        if not m:
            raise ValueError('Invalid version number: {0}'.format(vstr))

        version, suffix = m.groups()
        parts = self._parse_dotted_string(version)
        self.major = parts.pop(0)
        if len(parts):
            self.minor = parts.pop(0)
        if len(parts):
            self.patch = parts.pop(0)
        if not len(parts) == 0:
            raise ValueError('Invalid version (too long): {0}'.format(vstr))

        if suffix:
            # Build info
            idx = suffix.find('+')
            if idx > -1:
                self.build = suffix[idx+1:]
                suffix = suffix[:idx]
            if suffix:
                if not suffix.startswith('-'):
                    raise ValueError(
                        'Invalid suffix: `{0}`. Must start with `-`'.format(
                            suffix))
                self.suffix = suffix[1:]

        # wf().logger.debug('version str `{}` -> {}'.format(vstr, repr(self)))

    def _parse_dotted_string(self, s):
        """Parse string ``s`` into list of ints and strings"""
        parsed = []
        parts = s.split('.')
        for p in parts:
            if p.isdigit():
                p = int(p)
            parsed.append(p)
        return parsed

    @property
    def tuple(self):
        """Return version number as a tuple of major, minor, patch, pre-release
        """

        return (self.major, self.minor, self.patch, self.suffix)

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Not a Version instance: {0!r}'.format(other))
        t = self.tuple[:3]
        o = other.tuple[:3]
        if t < o:
            return True
        if t == o:  # We need to compare suffixes
            if self.suffix and not other.suffix:
                return True
            if other.suffix and not self.suffix:
                return False
            return (self._parse_dotted_string(self.suffix) <
                    self._parse_dotted_string(other.suffix))
        # t > o
        return False

    def __eq__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Not a Version instance: {0!r}'.format(other))
        return self.tuple == other.tuple

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Not a Version instance: {0!r}'.format(other))
        return other.__lt__(self)

    def __le__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Not a Version instance: {0!r}'.format(other))
        return not other.__lt__(self)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __str__(self):
        vstr = '{0}.{1}.{2}'.format(self.major, self.minor, self.patch)
        if self.suffix:
            vstr += '-{0}'.format(self.suffix)
        if self.build:
            vstr += '+{0}'.format(self.build)
        return vstr

    def __repr__(self):
        return "Version('{0}')".format(str(self))


####################################################################
# Logging helpers
####################################################################

def get_logger(name):
    """Get :class:`logging.Logger` for ``name``

    Ensures at least a :class:`logging.NullHandler` is set.

    """
    logger = logging.getLogger(name)
    # Ensure a handler is set on root to avoid warnings
    root = logging.getLogger('')
    if len(root.handlers) == 0:
        root.addHandler(NullHandler())

    return logger


def init_logging(console=True, logfile=None, level=logging.INFO):
    """Add handlers to root logger and set log level"""
    fmt_str = ('%(asctime)s %(filename)s:%(lineno)s'
               ' %(levelname)-8s %(message)s')
    logger = logging.getLogger('')
    logger.handlers = []
    if console:
        hdlr = logging.StreamHandler()
        hdlr.aw_handler = True
        fmt = logging.Formatter(fmt_str, datefmt='%H:%M:%S')
        hdlr.setFormatter(fmt)
        logger.addHandler(hdlr)

    if logfile is not None:
        logfile = os.path.abspath(logfile)
        hdlr = logging.handlers.RotatingFileHandler(logfile,
                                                    maxBytes=1024*1024,
                                                    backupCount=0)
        hdlr.aw_handler = True
        fmt = logging.Formatter(fmt_str, datefmt='%H:%M:%S')
        hdlr.setFormatter(fmt)
        logger.addHandler(hdlr)

    logger.setLevel(level)
