#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-01
#

"""Unit tests for :mod:`workflow.Workflow`."""



import logging
import os
import sys

from unicodedata import normalize

import pytest

from workflow import Workflow

from .conftest import env


def test_args(alfred4):
    """ARGV"""
    args = ['arg1', 'arg2', 'füntíme']
    oargs = sys.argv[:]
    sys.argv = [oargs[0]] + [s.encode('utf-8') for s in args]
    wf = Workflow()
    try:
        assert wf.args == args
    finally:
        sys.argv = oargs[:]


def test_arg_normalisation(alfred4):
    """ARGV normalisation"""
    def nfdme(s):
        """NFD-normalise string"""
        return normalize('NFD', s)

    args = [nfdme(s) for s in ['arg1', 'arg2', 'füntíme']]
    oargs = sys.argv[:]
    sys.argv = [oargs[0]] + [s.encode('utf-8') for s in args]

    wf = Workflow(normalization='NFD')
    try:
        assert wf.args == args
    finally:
        sys.argv = oargs[:]


def test_magic_args(alfred4):
    """Magic args"""
    # cache original sys.argv
    oargs = sys.argv[:]

    # delsettings
    sys.argv = [oargs[0]] + [b'workflow:delsettings']
    try:
        wf = Workflow(default_settings={'arg1': 'value1'})
        assert wf.settings['arg1'] == 'value1'
        assert os.path.exists(wf.settings_path)
        with pytest.raises(SystemExit):
            wf.args
        assert not os.path.exists(wf.settings_path)
    finally:
        sys.argv = oargs[:]

    # delcache
    sys.argv = [oargs[0]] + [b'workflow:delcache']

    def somedata():
        return {'arg1': 'value1'}

    try:
        wf = Workflow()
        cachepath = wf.cachefile('somedir')
        os.makedirs(cachepath)
        wf.cached_data('test', somedata)
        assert os.path.exists(wf.cachefile('test.pickle'))
        with pytest.raises(SystemExit):
            wf.args
        assert not os.path.exists(wf.cachefile('test.pickle'))
    finally:
        sys.argv = oargs[:]


def test_logger(wf):
    """Logger"""
    assert isinstance(wf.logger, logging.Logger)
    logger = logging.Logger('')
    wf.logger = logger
    assert wf.logger == logger


def test_icons():
    """Icons"""
    import workflow
    for name in dir(workflow):
        if name.startswith('ICON_'):
            path = getattr(workflow, name)
            print((name, path))
            assert os.path.exists(path)


@pytest.mark.parametrize('state,expected', [
        ('', False),
        ('0', False),
        ('1', True),
    ])
def test_debugging(alfred4, state, expected):
    """Debugging"""
    with env(alfred_debug=state, PYTEST_RUNNING=''):
        wf = Workflow()
        assert wf.debugging == expected, "unexpected debugging"


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
