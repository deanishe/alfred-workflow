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

import os

import pytest

from workflow._env import WorkflowEnvironment
from workflow.base import Version

from util import (
    WorkflowEnv,
    ALFRED_ENVVARS,
    WORKFLOW_NAME,
    BUNDLE_ID,
    DATADIR,
    CACHEDIR,
)


def test_env():
    """Env: env vars"""
    with WorkflowEnv(info_plist=False):
        e = WorkflowEnvironment()
        assert ALFRED_ENVVARS['alfred_preferences'] == e.preferences
        assert ALFRED_ENVVARS['alfred_preferences'] == e['preferences']
        assert (ALFRED_ENVVARS['alfred_preferences_localhash'] ==
                e.preferences_localhash)
        assert (ALFRED_ENVVARS['alfred_preferences_localhash'] ==
                e['preferences_localhash'])
        assert ALFRED_ENVVARS['alfred_theme'] == e.theme
        assert ALFRED_ENVVARS['alfred_theme'] == e['theme']
        assert (ALFRED_ENVVARS['alfred_theme_background'] ==
                e.theme_background)
        assert (ALFRED_ENVVARS['alfred_theme_background'] ==
                e['theme_background'])
        assert int(ALFRED_ENVVARS['alfred_theme_subtext']) == e.theme_subtext
        assert (int(ALFRED_ENVVARS['alfred_theme_subtext']) ==
                e['theme_subtext'])
        assert isinstance(e.alfred_version, Version)
        assert isinstance(e['alfred_version'], Version)
        assert Version(ALFRED_ENVVARS['alfred_version']) == e.alfred_version
        assert Version(ALFRED_ENVVARS['alfred_version']) == e['alfred_version']
        assert int(ALFRED_ENVVARS['alfred_version_build']) == e.alfred_build
        assert int(ALFRED_ENVVARS['alfred_version_build']) == e['alfred_build']
        assert ALFRED_ENVVARS['alfred_workflow_uid'] == e.uid
        assert ALFRED_ENVVARS['alfred_workflow_uid'] == e['uid']


def test_attributes():
    """Env: get as attributes"""
    with WorkflowEnv(info_plist=False):
        e = WorkflowEnvironment()
        with pytest.raises(AttributeError):
            e.log


def test_items():
    """Env get as items"""
    with WorkflowEnv(info_plist=False):
        e = WorkflowEnvironment()
        with pytest.raises(KeyError):
            e['smell']


def test_info():
    """Env: parse info.plist"""
    with WorkflowEnv(info_plist=True, env_default=False):
        e = WorkflowEnvironment()
        assert e.bundleid == BUNDLE_ID
        assert e.bundleid == BUNDLE_ID
        assert e['name'] == WORKFLOW_NAME
        assert e['name'] == WORKFLOW_NAME


def test_generated():
    """Env: generated vars"""
    with WorkflowEnv(version='1.2.5', env_default=False):
        e = WorkflowEnvironment()
        assert e.datadir == DATADIR
        assert e.cachedir == CACHEDIR
        assert e.workflowdir == os.path.abspath(os.getcwdu())
        assert e.logfile == os.path.join(CACHEDIR, '{0}.log'.format(BUNDLE_ID))
        assert e.version == Version('1.2.5')


def test_fails_with_no_files():
    """Env: fails with no info.plist/version"""
    with WorkflowEnv(info_plist=False):
        e = WorkflowEnvironment()
        with pytest.raises(EnvironmentError):
            e.workflowdir
        assert e.version is None


if __name__ == '__main__':
    pytest.main([__file__])
