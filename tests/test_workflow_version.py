#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-09-10
#

"""
"""

from __future__ import print_function, unicode_literals

import os
import pytest

from util import create_info_plist, delete_info_plist, INFO_PLIST_TEST3

from workflow.workflow3 import Workflow3
from workflow.update import Version


@pytest.fixture(scope='module')
def info3(request):
    """Ensure `info.plist` exists in the working directory."""
    create_info_plist(INFO_PLIST_TEST3)
    request.addfinalizer(delete_info_plist)


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
