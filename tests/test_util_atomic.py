#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""Unit tests for :func:`~workflow.util.atomic_writer`."""



import json
import os

import pytest

from .util import DEFAULT_SETTINGS

from workflow.util import atomic_writer


def _settings(tempdir):
    """Path to ``settings.json`` file."""
    return os.path.join(tempdir, 'settings.json')


def test_write_file_succeed(tempdir):
    """Succeed, no temp file left"""
    p = _settings(tempdir)
    with atomic_writer(p, 'w') as fp:
        json.dump(DEFAULT_SETTINGS, fp)

    assert len(os.listdir(tempdir)) == 1
    assert os.path.exists(p)


def test_failed_before_writing(tempdir):
    """Exception before writing"""
    p = _settings(tempdir)

    def write():
        with atomic_writer(p, 'w'):
            raise Exception()

    with pytest.raises(Exception):
        write()

    assert not os.listdir(tempdir)


def test_failed_after_writing(tempdir):
    """Exception after writing"""
    p = _settings(tempdir)

    def write():
        with atomic_writer(p, 'w') as fp:
            json.dump(DEFAULT_SETTINGS, fp)
            raise Exception()

    with pytest.raises(Exception):
        write()

    assert not os.listdir(tempdir)


def test_failed_without_overwriting(tempdir):
    """AtomicWriter: Exception after writing won't overwrite the old file"""
    p = _settings(tempdir)
    mockSettings = {}

    def write():
        with atomic_writer(p, 'w') as fp:
            json.dump(mockSettings, fp)
            raise Exception()

    with atomic_writer(p, 'w') as fp:
        json.dump(DEFAULT_SETTINGS, fp)

    assert len(os.listdir(tempdir)) == 1
    assert os.path.exists(p)

    with pytest.raises(Exception):
        write()

    assert len(os.listdir(tempdir)) == 1
    assert os.path.exists(p)

    with open(p, 'rb') as fp:
        real_settings = json.load(fp)

    assert DEFAULT_SETTINGS == real_settings


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
