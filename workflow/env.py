#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-24
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import plistLib

from workflow import util
from workflow.base import get_logger

log = get_logger(__name__)

#: Root directory for workflow data directories. Workflows should
#: store their data in ``<bundleid>`` subdirectories.
DATA_ROOT = os.path.join(os.path.expanduser(
    '~/Library/Application Support/Alfred 2/Workflow Data'))
#: Root directory for workflow cache directories. Workflows should
#: store their data in ``<bundleid>`` subdirectories.
CACHE_ROOT = os.path.join(os.path.expanduser(
    '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data'))

#: Names of the environmental variables set by Alfred
ALFRED_ENVVARS = (
    'alfred_preferences',
    'alfred_preferences_localhash',
    'alfred_theme',
    'alfred_theme_background',
    'alfred_theme_subtext',
    'alfred_version',
    'alfred_version_build',
    'alfred_workflow_bundleid',
    'alfred_workflow_cache',
    'alfred_workflow_data',
    'alfred_workflow_name',
    'alfred_workflow_uid',
)

#: Environmental variables that should be converted to integers
ALFRED_ENVVARS_INT = ('alfred_version_build', 'alfred_theme_subtext')

# Data parsed from info.plist
_info = None
# Alfred's environmental variables
_alfred_env = None
# This workflow's bundle ID
_bundleid = None
# This workflow's name
_workflow_name = None


def get_info():
    """Return contents of ``info.plist``"""
    global _info
    if _info is None:
        path = os.path.join(get_workflowdir(), 'info.plist')
        _info = plistLib.readPlist(path)
    return _info


def get_alfred_env():
    """Return dict of Alfred's environmental variables

    The ``alfred_`` prefix is stripped from the variable names.

    """

    global _alfred_env

    if _alfred_env is None:
        data = {}
        for key in ALFRED_ENVVARS:
            value = os.getenv(key)

            if isinstance(value, str):
                if key in ALFRED_ENVVARS_INT:
                    value = int(value)
                else:
                    value = util.decode(value)

            data[key[7:]] = value

        _alfred_env = data

    return _alfred_env


def _env_or_info(envname, infoname):
    """Read value from either Alfred env vars or ``info.plist``

    :param envname: Name of environmental var to check
    :type envname: string
    :param infoname: Name of key in ``info.plist`` to check
    :type infoname: string
    :returns: ``unicode`` value

    """

    if get_alfred_env().get(envname) is not None:
        return get_alfred_env().get(envname)
    return util.decode(get_info()[infoname])


def get_bundleid():
    """Return workflow's bundle ID"""
    global _bundleid

    if _bundleid is None:
        _bundleid = _env_or_info('workflow_bundleid', 'bundleid')

    return _bundleid


def get_datadir():
    """Return path to workflow's data directory"""
    if get_alfred_env().get('workflow_data') is not None:
        dirpath = get_alfred_env().get('workflow_data')
    else:
        dirpath = os.path.join(DATA_ROOT, get_bundleid())

    return util.create_directory(dirpath)


def get_cachedir():
    """Return path to workflow's cache directory"""
    if get_alfred_env().get('workflow_cache') is not None:
        dirpath = get_alfred_env().get('workflow_cache')
    else:
        dirpath = os.path.join(CACHE_ROOT, get_bundleid())

    return util.create_directory(dirpath)


def get_workflowdir():
    """Return path to workflow's root directory"""
    path = util.find_upwards('info.plist')
    if path is None:
        raise EnvironmentError("`info.plist` not found in directory tree")
    return os.path.dirname(path)


def get_name():
    """Return name of this workflow"""
    global _workflow_name
    if _workflow_name is None:
        _workflow_name = _env_or_info('workflow_name', 'name')

    return _workflow_name
