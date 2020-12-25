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



from contextlib import contextmanager
import os
from shutil import rmtree
from tempfile import mkdtemp

import pytest
from workflow.workflow import Workflow


from .util import (
    INFO_PLIST_TEST,
    INFO_PLIST_TEST3,
    InfoPlist,
)

BUNDLE_ID = 'net.deanishe.alfred-workflow'
WORKFLOW_NAME = 'Alfred-Workflow Test'
WORKFLOW_VERSION = '1.1.1'

ENV_V2 = dict(
    alfred_version='2.4',
    alfred_version_build='277',
    alfred_workflow_version=WORKFLOW_VERSION,
    alfred_workflow_bundleid=BUNDLE_ID,
    alfred_workflow_name=WORKFLOW_NAME,
    alfred_workflow_cache=os.path.expanduser(
        '~/Library/Caches/com.runningwithcrayons.Alfred-2/'
        'Workflow Data/' + BUNDLE_ID),
    alfred_workflow_data=os.path.expanduser(
        '~/Library/Application Support/Alfred 2/'
        'Workflow Data/' + BUNDLE_ID),
    alfred_preferences=os.path.expanduser(
        '~/Library/Application Support/Alfred 2/'
        'Alfred.alfredpreferences'),
)

ENV_V3 = dict(
    alfred_version='3.8.1',
    alfred_version_build='961',
    alfred_workflow_version=WORKFLOW_VERSION,
    alfred_workflow_bundleid=BUNDLE_ID,
    alfred_workflow_name=WORKFLOW_NAME,
    alfred_workflow_cache=os.path.expanduser(
        '~/Library/Caches/com.runningwithcrayons.Alfred-3/'
        'Workflow Data/' + BUNDLE_ID),
    alfred_workflow_data=os.path.expanduser(
        '~/Library/Application Support/Alfred 3/'
        'Workflow Data/' + BUNDLE_ID),
    alfred_preferences=os.path.expanduser(
        '~/Library/Application Support/Alfred 3/'
        'Alfred.alfredpreferences'),
)

ENV_V4 = dict(
    alfred_version='4.0',
    alfred_version_build='1061',
    alfred_workflow_version=WORKFLOW_VERSION,
    alfred_workflow_bundleid=BUNDLE_ID,
    alfred_workflow_name=WORKFLOW_NAME,
    alfred_workflow_cache=os.path.expanduser(
        '~/Library/Caches/com.runningwithcrayons.Alfred/'
        'Workflow Data/' + BUNDLE_ID),
    alfred_workflow_data=os.path.expanduser(
        '~/Library/Application Support/Alfred/'
        'Workflow Data/' + BUNDLE_ID),
    alfred_preferences=os.path.expanduser(
        '~/Library/Application Support/Alfred/'
        'Alfred.alfredpreferences'),
)

COMMON = dict(
    alfred_debug='1',
    alfred_preferences_localhash='adbd4f66bc3ae8493832af61a41ee609b20d8705',
    alfred_theme='alfred.theme.yosemite',
    alfred_theme_background='rgba(255,255,255,0.98)',
    alfred_theme_subtext='3',
    alfred_workflow_uid='user.workflow.B0AC54EC-601C-479A-9428-01F9FD732959',
)


@contextmanager
def env(**kwargs):
    """Context manager to alter and restore system environment."""
    prev = os.environ.copy()
    for k, v in list(kwargs.items()):
        if v is None:
            if k in os.environ:
                del os.environ[k]
        else:
            os.environ[k] = str(v)

    yield

    os.environ = prev


@pytest.fixture
def wf(alfred4, infopl):
    """Provide a Workflow using Alfred 4 configuration."""
    wf = Workflow()
    yield wf
    wf.reset()


def setenv(*dicts):
    """Update ``os.environ`` from ``dict``s."""
    for d in dicts:
        os.environ.update(d)


def cleanenv():
    """Remove Alfred variables from ``os.environ``."""
    for k in list(os.environ.keys()):
        if k.startswith('alfred_'):
            del os.environ[k]


@pytest.fixture(scope='function')
def alfred3():
    """Context manager that sets Alfred 3 environment variables."""
    cleanenv()
    setenv(COMMON, ENV_V3)
    yield
    cleanenv()


@pytest.fixture(scope='function')
def alfred4():
    """Context manager that sets Alfred 4 environment variables."""
    cleanenv()
    setenv(COMMON, ENV_V4)
    yield
    cleanenv()


@pytest.fixture(scope='function')
def tempdir():
    """Create (and delete) a temporary directory."""
    path = mkdtemp()
    yield path
    if os.path.exists(path):
        rmtree(path)


@pytest.fixture()
def infopl2():
    """Ensure ``info.plist`` exists in the working directory."""
    with InfoPlist(INFO_PLIST_TEST):
        yield


@pytest.fixture()
def infopl():
    """Ensure ``info.plist`` exists in the working directory."""
    with InfoPlist(INFO_PLIST_TEST3):
        yield
