#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""Common pytest fixtures."""

from __future__ import print_function, absolute_import

import os
from shutil import rmtree
from tempfile import mkdtemp

import pytest

from .util import (
    INFO_PLIST_TEST,
    INFO_PLIST_TEST3,
    InfoPlist,
)


@pytest.fixture(scope='function')
def tempdir():
    """Create (and delete) a temporary directory."""
    path = mkdtemp()
    yield path
    if os.path.exists(path):
        rmtree(path)


@pytest.fixture(scope='module')
def info2():
    """Ensure ``info.plist`` exists in the working directory."""
    os.environ['alfred_version'] = '2.4'
    with InfoPlist(INFO_PLIST_TEST):
        yield
    del os.environ['alfred_version']


@pytest.fixture(scope='module')
def info3():
    """Ensure ``info.plist`` exists in the working directory."""
    os.environ['alfred_version'] = '3.2'
    with InfoPlist(INFO_PLIST_TEST3):
        yield
    del os.environ['alfred_version']
