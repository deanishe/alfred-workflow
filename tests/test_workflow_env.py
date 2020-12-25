# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created 2019-05-05

"""Unit tests for environment/info.plist."""



import logging
import os

import pytest

from workflow.workflow import Workflow

from .conftest import (
    env, COMMON, ENV_V4,
    BUNDLE_ID, WORKFLOW_NAME,
)
from .util import INFO_PLIST_PATH, dump_env


def test_file(infopl):
    """info.plist"""
    wf = Workflow()
    assert wf.name == WORKFLOW_NAME
    assert wf.bundleid == BUNDLE_ID


def test_file_missing():
    """Info.plist missing"""
    wf = Workflow()
    assert not os.path.exists(INFO_PLIST_PATH)
    with pytest.raises(IOError):
        wf.workflowdir


def test_env(wf):
    """Alfred environmental variables"""
    env = COMMON.copy()
    env.update(ENV_V4)
    for k, v in list(env.items()):
        k = k.replace('alfred_', '')
        if k in ('debug', 'version_build', 'theme_subtext'):
            assert int(v) == wf.alfred_env[k]
        else:
            assert isinstance(wf.alfred_env[k], str)
            assert str(v) == wf.alfred_env[k]

    assert wf.datadir == env['alfred_workflow_data']
    assert wf.cachedir == env['alfred_workflow_cache']
    assert wf.bundleid == env['alfred_workflow_bundleid']
    assert wf.name == env['alfred_workflow_name']


def test_alfred_debugger(alfred4):
    """Alfred debugger status"""
    # With debugger on
    with env(alfred_debug='1', PYTEST_RUNNING=None):
        dump_env()
        wf = Workflow()
        assert wf.debugging, "Alfred's debugger not open"
        assert wf.logger.getEffectiveLevel() == logging.DEBUG
        wf.reset()

    # With debugger off
    with env(alfred_debug=None, PYTEST_RUNNING=None):
        dump_env()
        wf = Workflow()
        assert not wf.debugging, "Alfred's debugger is not closed"
        assert wf.logger.getEffectiveLevel() == logging.INFO
        wf.reset()
