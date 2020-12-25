#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""Unit tests for :mod:`workflow.background`."""



import os, sys
from time import sleep

import pytest

from workflow import Workflow
from workflow.background import is_running, kill, run_in_background


def _pidfile(name):
    return Workflow().cachefile('{0}.pid'.format(name))


def _write_pidfile(name, pid):
    pidfile = _pidfile(name)
    with open(pidfile, 'wb') as file:
        file.write(pid.to_bytes(4, sys.byteorder))


def _delete_pidfile(name):
    pidfile = _pidfile(name)
    if os.path.exists(pidfile):
        os.unlink(pidfile)


@pytest.mark.usefixtures('infopl')
class TestBackground(object):
    """Unit tests for background jobs."""

    def test_no_pidfile(self):
        """No PID file for non-existent job"""
        assert not is_running('boomstick')

    def test_non_existent_process(self):
        """Non-existent process"""
        _write_pidfile('test', 9999999)
        assert not is_running('test')
        assert not os.path.exists(_pidfile('test'))

    def test_existing_process(self):
        """Existing process"""
        _write_pidfile('test', os.getpid())
        try:
            assert is_running('test')
            assert os.path.exists(_pidfile('test'))
        finally:
            _delete_pidfile('test')

    def test_run_in_background(self):
        """Run in background"""
        cmd = ['sleep', '0.01']
        assert run_in_background('test', cmd) == 0
        assert is_running('test')
        assert os.path.exists(_pidfile('test'))
        # Already running
        assert run_in_background('test', cmd) is None
        sleep(0.1)  # wait for job to finish
        assert not is_running('test')
        assert not os.path.exists(_pidfile('test'))

    def test_kill(self):
        """Kill"""
        assert kill('test') is False
        cmd = ['sleep', '0.01']
        assert run_in_background('test', cmd) == 0
        assert is_running('test')
        assert kill('test') is True
        sleep(0.1)  # give process time to exit
        assert not is_running('test')


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
