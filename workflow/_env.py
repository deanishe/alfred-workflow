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

import functools
import os
import plistlib

from workflow import __version__
from workflow import util
from workflow.base import get_logger, Version

log = get_logger(__name__)

#: Root directory for workflow data directories. Workflows should
#: store their data in ``<bundleid>`` subdirectories.
data_root = os.path.join(os.path.expanduser(
    '~/Library/Application Support/Alfred 2/Workflow Data'))
#: Root directory for workflow cache directories. Workflows should
#: store their data in ``<bundleid>`` subdirectories.
cache_root = os.path.join(os.path.expanduser(
    '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data'))


# _env = None


# def _e():
#     global _env
#     if _env is None:
#         _env = WorkflowEnvironment()
#     return _env


# def get(key, default=None):
#     return _e().get(key)


class WorkflowEnvironment(dict):
    """Lazy-loading dictionary of workflow-related environmental vars


    """

    # Template for loading values. Keys are the eventual attribute
    # names/keys. Values are 3-tuples, processed in same order:
    #
    #    1. Name of corresponding envvar
    #    2. Name of key in info.plist or in class method (_get_{name})
    #    3. Post-processor callable. Called on any value retrieved
    #
    # Values from envvars are populated immediately, others are
    # populated lazily. If an envvar isn't found, it will fall back
    # to info.plist/getter method.
    _vars = {
        # name, env varname, info.plist/method name, post-processor
        'info': (None, None, None),
        'logfile': (None, None, None),
        'preferences': ('alfred_preferences', None, util.decode),
        'preferences_localhash': ('alfred_preferences_localhash',
                                  None, util.decode),
        'theme': ('alfred_theme', None, util.decode),
        'theme_background': ('alfred_theme_background', None, util.decode),
        'theme_subtext': ('alfred_theme_subtext', None, int),
        'alfred_version': ('alfred_version', None, Version),
        'alfred_build': ('alfred_version_build', None, int),
        'uid': ('alfred_workflow_uid', None, util.decode),
        'bundleid': ('alfred_workflow_bundleid', 'bundleid', util.decode),
        'name': ('alfred_workflow_name', 'name', util.decode),
        'cachedir': ('alfred_workflow_cache', None,
                     util.decode),
        'datadir': ('alfred_workflow_data', None, util.decode),
        'workflowdir': (None, None, util.decode),
        'version': (None, None, None),
    }

    def __init__(self, *args, **kwargs):
        super(WorkflowEnvironment, self).__init__(*args, **kwargs)
        # self.__dict__ = self
        self._info = None
        # Need to alias these here as they will disappear from the
        # local namespace when `sys.modules` is messed with below
        self._getitem = super(WorkflowEnvironment, self).__getitem__
        self._cache_root = cache_root
        self._data_root = data_root
        self._version = Version
        self['aw_version'] = Version(__version__)
        # Map varnames to loaders for lazy loading
        # {name: (getfunc, postfunc), ...}
        self._loaders = {}

        # Load environmental variables and store lazy loaders
        # for info.plist ones
        for name in self._vars:
            envname, alt, post = self._vars[name]
            value = None
            # Try to load variable from environment
            if envname:
                value = os.getenv(envname)

            if value is not None:
                if post is not None:
                    value = post(value)
                log.debug('Setting from environment : {0} = {1!r}'.format(name,
                          value))
                self[name] = value
            # Defer loading till needed
            else:
                func = None
                if alt is not None:  # Fetch from info.plist
                    func = functools.partial(self.getinfo, alt)
                    func.__name__ = 'info.plist[{0}]'.format(alt)
                else:  # Find generator method
                    methname = '_get_{0}'.format(name)
                    if hasattr(self, methname):
                        func = getattr(self, methname)
                    else:
                        # TODO: collect unset vars and log a WARNING
                        # telling user to update Alfred
                        log.warning('Unset environmental var : {0}'.format(
                                    name))

                if func is not None:
                    self._loaders[name] = (func, post)
                    log.debug('Lazy loader for `{0}` : {1}'.format(name,
                              func.__name__))

                else:  # TODO: is defaulting to `None` correct?
                    self[name] = None

    def __getattr__(self, attr):
        if attr in self or attr in self._vars:
            return self[attr]
        elif attr in globals():
            return globals()[attr]
        else:
            raise AttributeError('{0!r}'.format(attr))

    def __getitem__(self, key):
        getitem = super(WorkflowEnvironment, self).__getitem__
        if key in self:  # Already in dict
            return getitem(key)

        if key in self._loaders:  # Lazy-loading
            loader, post = self._loaders[key]
            # log.debug('Loading `{0}` with {1!r}'.format(key,
            #           loader.__name__))
            value = loader()
            log.debug('Loaded `{0}` with `{1}` : {2!r}'.format(
                      key, loader.__name__, value))
            if post is not None:
                value = post(value)
            self[key] = value
            return value
        # Fall back to superclass
        return getitem(key)

    def _get_info(self):
        """The parsed contents of ``info.plist``"""
        path = os.path.join(self['workflowdir'], 'info.plist')
        log.debug('Reading {0} ...'.format(path))
        return plistlib.readPlist(path)

    def getinfo(self, key):
        return self['info'].get(key)

    def _get_cachedir(self):
        dirpath = os.path.join(self._cache_root, self['bundleid'])
        return dirpath

    def _get_datadir(self):
        dirpath = os.path.join(self._data_root, self['bundleid'])
        return dirpath

    def _get_logfile(self):
        filepath = os.path.join(self['cachedir'],
                                '{0}.log'.format(self['bundleid']))
        return filepath

    def _get_workflowdir(self):
        path = util.find_upwards('info.plist')
        if path is None:
            raise EnvironmentError(
                '`info.plist` not found in directory tree')
        return os.path.dirname(path)

    def _get_version(self):
        path = util.find_upwards('version')
        if path is None:
            return None
        with open(path, 'rb') as fp:
            return Version(fp.read())
