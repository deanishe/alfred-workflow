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
Simple plugin management/registration system.

"""

from __future__ import print_function, unicode_literals, absolute_import

import os

from workflow import base, util

log = base.get_logger(__name__)

_plugins = {}
_plugin_paths = []


def get_plugin(name):
    """Return registered plugin for ``name`` or ``None``"""
    return _plugins.get(name)


def get_plugins():
    """Return all registered plugins"""
    return _plugins.values()


def add_plugin_path(path):
    """Add ``path`` to search path for plugins"""
    global _plugin_paths
    if path not in _plugin_paths:
        _plugin_paths.append(path)


def _find_plugins(dirpath):
    """Return modules and packages in directory ``dirpath``

    :param dirpath: Path to directory to search for Python modules and
        packages.
    :returns: List of 2-tuples ``(name, path)``

    """

    plugins = []
    for name in os.listdir(dirpath):
        path = os.path.join(dirpath, name)
        if name.lower().endswith('.py') and os.path.isfile(path):
            plugins.append((name[:-3], path))
        elif os.path.isdir(path):  # Check if it's a Python package
            if os.path.exists(os.path.join(path, '__info__.py')):
                plugins.append((name, path))

    return plugins


def init_plugins(names=None):
    """Load all plugins in configured plugin directories

    :param names: Names of plugins to load. If not specified, all plugins
        will be loaded.
    :type names: list or tuple

    """


    # Ensure default plugins are loaded last so they can be overridden
    # and have lowest priority
    dirpaths = _plugin_paths[:] + [base.DEFAULT_PLUGIN_PATH]

    with util.syspath(dirpaths):

        for dirpath in dirpaths:
            for name, path in _find_plugins(dirpath):

                if names is not None:
                    if name not in names:
                        continue

                if name in _plugins:
                    log.warning(
                        'Plugin with name `{0}` already exists'.format(name))
                    continue

                try:
                    plugin = __import__(name, globals(), locals(), [], -1)
                except ImportError as err:
                    log.error('Cannot load plugin `{0}` ({1}) : {2}'.format(
                              name, path, err))
                    continue
                else:
                    log.debug('Loaded plugin `{0}` ({1})'.format(name, path))

            plugin.register()
            _plugins[name] = plugin
