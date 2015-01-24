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

from contextlib import contextmanager
import os
import sys

from workflow import base

log = base.get_logger(__name__)

_plugins = {}
_plugin_paths = [os.path.join(os.path.dirname(__file__), 'plugins')]


@contextmanager
def syspath(paths):
    """Temporarily adds ``paths`` to front of :data:`sys.path`"""
    _syspath = sys.path[:]
    for path in paths:
        sys.path.insert(0, path)
    yield
    sys.path = _syspath


def get_plugin(name):
    """Return registered plugin for ``name`` or ``None``"""
    global _plugins
    return _plugins.get(name)


def add_plugin_path(path):
    """Add ``path`` to search path for plugins"""
    global _plugin_paths
    if path not in _plugin_paths:
        _plugin_paths.append(path)


def load_plugin(name):
    """Load specified plugin from the configured plugin paths"""
    load_plugins([name])


def load_plugins(names):
    """Load specifed plugins from the configured plugin paths"""
    global _plugins, _plugin_paths

    with syspath(_plugin_paths):

        for name in names:
            if name in _plugins:
                log.warning(
                    'Plugin with name `{0}` already exists'.format(name))
                continue

            try:
                plugin = __import__(name, globals(), locals(), [], -1)
            except ImportError as err:
                log.error('Cannot load plugin `{0}` : {1}'.format(name, err))
                continue

            plugin.register()
            _plugins[name] = plugin
