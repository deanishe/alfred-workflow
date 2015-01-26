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
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import shutil
import sys
import tempfile
from unicodedata import normalize

import pytest

from workflow import util

LIB_PATH = os.path.join(os.path.dirname(__file__), 'lib')


@pytest.fixture
def tempdir(request):
    path = tempfile.mkdtemp()

    def rm():
        if os.path.exists(path):
            shutil.rmtree(path)

    request.addfinalizer(rm)

    return path


def test_syspath():
    """Manipulate `sys.path`"""
    if LIB_PATH in sys.path:
        sys.path.remove(LIB_PATH)
    assert LIB_PATH not in sys.path
    with util.syspath([LIB_PATH]):
        assert LIB_PATH in sys.path
        assert sys.path[0] == LIB_PATH
    assert LIB_PATH not in sys.path


def test_create_dir(tempdir):
    """Create directory"""
    d1 = os.path.join(tempdir, 'd1')
    d2 = os.path.join(d1, 'd2')
    res = util.create_directory(d2)
    assert res == d2
    assert os.path.exists(d2)


def test_find_upwards(tempdir):
    """Find upwards"""
    name = 'aintnofilebythis.name.nosiree'
    start = os.path.join(tempdir, '1', '2', '3')
    os.makedirs(start)

    assert util.find_upwards(name, start) is None

    fpath = os.path.join(tempdir, name)
    with open(fpath, 'wb') as fp:
        fp.write(name)

    assert util.find_upwards(name, start) == fpath

    fpath = os.path.join(start, name)
    with open(fpath, 'wb') as fp:
        fp.write(name)

    assert util.find_upwards(name, start) == fpath

    curdir = os.getcwdu()
    try:
        os.chdir(start)
        assert util.find_upwards(name) == os.path.realpath(fpath)
    finally:
        os.chdir(curdir)


def test_decode():
    """Decode text"""
    utf8 = b'Jürgen'
    u = 'Jürgen'
    assert util.decode(utf8) == u
    assert util.decode(u) == u
    u2 = normalize('NFD', u)
    assert u != u2
    assert util.decode(u, normalization='NFD') == u2


def test_symbols():
    """Symbols"""
    test1a = util.symbol('test1')
    test1b = util.symbol('test1')
    test2a = util.symbol('test2')
    test2b = util.symbol('test2')
    assert test1a is test1b
    assert test1a is not test2a
    assert test2a is test2b
    assert repr(test1a) == 'test1'


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
