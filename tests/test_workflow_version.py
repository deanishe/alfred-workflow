#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-09-10
#

"""Unit tests for workflow version determination."""

from __future__ import print_function, unicode_literals

import os
import pytest

from workflow.workflow3 import Workflow3
from workflow.update import Version


def test_version_info_plist(info3):
    """Version from info.plist."""
    wf = Workflow3()
    assert wf.version == Version('1.1.1')


def test_version_envvar(info3):
    """Version from environment variable."""
    os.environ['alfred_workflow_version'] = '1.1.2'
    wf = Workflow3()
    try:
        assert wf.version == Version('1.1.2')
    finally:
        del os.environ['alfred_workflow_version']


def test_version_update_settings(info3):
    """Version from update_settings."""
    wf = Workflow3(update_settings={'version': '1.1.3'})
    assert wf.version == Version('1.1.3')


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
