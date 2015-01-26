#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-26
#

from __future__ import print_function, unicode_literals, absolute_import

import logging
import tempfile

import pytest

from workflow import base

invalid_versions = [
    'bob',
    '1.x.8',
    '1.0b',
    '1.0.3a',
    '1.0.0.0',
]
valid_versions = [
    ('1', '1.0.0'),
    ('1.9', '1.9.0'),
    ('10.0', '10.0.0'),
    '1.0.1',
    '2.2.1',
    '10.11.12',
    '9.99.9999',
    '12.333.0-alpha',
    '8.10.11',
    '9.4.3+20144353453',
    '3.1.4-beta+20144334',
]


########################################################################
# Version
########################################################################

def test_valid_versions():
    """Versions: valid version strings"""
    for v in valid_versions:
        if isinstance(v, tuple):
            vin, vout = v
        else:
            vin = vout = v
        assert str(base.Version(vin)) == vout
        assert str(base.Version('v{0}'.format(vin))) == vout


def test_invalid_verision():
    """Versions: invalid version strings"""
    for v in invalid_versions:
        with pytest.raises(ValueError):
            base.Version(v)


def test_compare_bad_objects():
    """Versions: invalid comparisons"""
    v = base.Version('1.0.0')
    t = (1, 0, 0)
    with pytest.raises(ValueError):
        v == t
    with pytest.raises(ValueError):
        v >= t
    with pytest.raises(ValueError):
        v <= t
    with pytest.raises(ValueError):
        v != t
    with pytest.raises(ValueError):
        v > t
    with pytest.raises(ValueError):
        v < t


def test_compare_versions():
    """Versions: comparisons"""
    assert base.Version('1') == base.Version('1.0') == base.Version('1.0.0')
    assert base.Version('1.0.0') == base.Version('01.0.00')
    assert base.Version('1.10.0') > base.Version('1.9.9')
    assert base.Version('1.10.0') > base.Version('1.10.0-alpha')
    assert base.Version('1.9.9') < base.Version('1.10.0')
    assert base.Version('1.10.0-alpha') < base.Version('1.10.0')
    assert base.Version('1.10.0') >= base.Version('1.9.9')
    assert base.Version('1.10.0') >= base.Version('1.10.0-alpha')
    assert base.Version('1.9.9') <= base.Version('1.10.0')
    assert base.Version('1.10.0-alpha') <= base.Version('1.10.0')
    assert base.Version('1.10.0-alpha') < base.Version('1.10.0-beta')
    assert base.Version('1.10.0-beta') > base.Version('1.10.0-alpha')
    assert base.Version('1.10.0-beta') != base.Version('1.10.0-alpha')
    assert base.Version('1.10.0-alpha') != base.Version('1.10.0')
    assert base.Version('2.10.20') > base.Version('1.20.30')
    assert base.Version('2.10.20') == base.Version('2.10.20+2342345345')
    # With v prefix
    assert base.Version('v1.0.0') == base.Version('01.0.00')
    assert base.Version('v1.10.0') > base.Version('1.9.9')
    assert base.Version('v1.10.0') > base.Version('1.10.0-alpha')
    assert base.Version('v1.9.9') < base.Version('1.10.0')
    assert base.Version('v1.10.0-alpha') < base.Version('1.10.0')
    assert base.Version('v1.10.0') >= base.Version('1.9.9')
    assert base.Version('v1.10.0') >= base.Version('1.10.0-alpha')
    assert base.Version('v1.9.9') <= base.Version('1.10.0')
    assert base.Version('v1.10.0-alpha') <= base.Version('1.10.0')
    assert base.Version('v1.10.0-alpha') < base.Version('1.10.0-beta')
    assert base.Version('v1.10.0-beta') > base.Version('1.10.0-alpha')
    assert base.Version('v1.10.0-beta') != base.Version('1.10.0-alpha')
    assert base.Version('v1.10.0-alpha') != base.Version('1.10.0')
    assert base.Version('v2.10.20') > base.Version('1.20.30')
    assert base.Version('v2.10.20') == base.Version('2.10.20+2342345345')
    # With and without suffixes
    assert base.Version('v1.10.0') > base.Version('1.10.0-beta')
    assert base.Version('v1.10.0-alpha') < base.Version('1.10.0-beta')
    # Complex suffixes
    assert base.Version('1.0.0-alpha') < base.Version('1.0.0-alpha.1')
    assert base.Version('1.0.0-alpha.1') < base.Version('1.0.0-alpha.beta')
    assert base.Version('1.0.0-alpha.beta') < base.Version('1.0.0-beta')
    assert base.Version('1.0.0-beta') < base.Version('1.0.0-beta.2')
    assert base.Version('1.0.0-beta.2') < base.Version('1.0.0-beta.11')
    assert base.Version('1.0.0-beta.11') < base.Version('1.0.0-rc.1')
    assert base.Version('1.0.0-rc.1') < base.Version('1.0.0')


def test_round_trip():
    """Versions: round-trip"""
    vstrs = ['1.0.0', '1.2.0-alpha', '2.4.5+dave', '2.1.2-beta+dave']
    for vstr in vstrs:
        v = base.Version(vstr)
        assert str(v) == vstr
        assert base.Version(vstr) == base.Version(str(v))

    # repr
    v = base.Version('1')
    assert repr(v) == "Version('1.0.0')"


########################################################################
# Logging
########################################################################

def test_logging():
    """Logging"""
    # Reset logging
    root = logging.getLogger('')
    root.handlers = [hdlr for hdlr in root.handlers if
                     not hasattr(hdlr, 'aw_handler')]
    print('{0} root handler(s)'.format(len(root.handlers)))

    logger = base.get_logger(__name__)
    # print('{0} handler(s) for `{1}`'.format(len(logger.handlers), __name__))
    assert len(logger.handlers) == 0
    # console only
    base.init_logging()
    root = logging.getLogger('')
    handlers = [hdlr for hdlr in root.handlers if hasattr(hdlr, 'aw_handler')]
    assert len(handlers) == 1
    # console and logfile
    logfile = tempfile.NamedTemporaryFile(suffix='.log')
    print(logfile.name)
    base.init_logging(logfile=logfile.name)
    root = logging.getLogger('')
    handlers = [hdlr for hdlr in root.handlers if hasattr(hdlr, 'aw_handler')]
    assert len(handlers) == 2
    # Remove all handlers
    base.init_logging(console=False)
    root = logging.getLogger('')
    assert len(root.handlers) == 0


if __name__ == '__main__':
    pytest.main([__file__])
