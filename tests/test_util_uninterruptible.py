#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""Unit tests for ``uninterruptible`` decorator."""



import os
import signal

import pytest

from workflow.util import uninterruptible


class Target(object):
    """Object to be manipulated by :func:`fakewrite`."""

    def __init__(self, kill=True, finished=False):
        """Create new `Target`."""
        self.kill = kill
        self.finished = finished
        self.handled = False

    def handler(self, signum, frame):
        """Alternate signal handler."""
        self.handled = True


@uninterruptible
def fakewrite(target):
    """Mock writer.

    Sets ``target.finished`` if it completes.

    Args:
        target (Target): Object to set status on
    """
    if target.kill:
        target.kill = False
        os.kill(os.getpid(), signal.SIGTERM)
    target.finished = True


@pytest.fixture(scope='function')
def target():
    """Create a `Target`."""
    # restore default handlers
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    yield Target()
    # restore default handlers
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


def test_normal(target):
    """Normal writing operator"""
    target.kill = False
    fakewrite(target)
    assert target.finished


def test_sigterm_signal(target):
    """Process is killed, but call completes"""
    with pytest.raises(SystemExit):
        fakewrite(target)

    # call has completed
    assert target.finished
    assert not target.kill


def test_old_signal_handler(target):
    """Kill with different signal handler registered"""
    signal.signal(signal.SIGTERM, target.handler)

    fakewrite(target)

    assert target.finished
    assert target.handled
    assert not target.kill


def test_old_signal_handler_restore(target):
    """Restore previous signal handler after write"""
    signal.signal(signal.SIGTERM, target.handler)
    target.kill = False

    fakewrite(target)

    assert target.finished
    assert signal.getsignal(signal.SIGTERM) == target.handler


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
