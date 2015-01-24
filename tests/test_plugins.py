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
import sys

from workflow import plugins

LIB_PATH = os.path.join(os.path.dirname(__file__), 'lib')


def test_syspath():
    """Manipulate `sys.path`"""
    assert LIB_PATH not in sys.path
    with plugins.syspath([LIB_PATH]):
        assert LIB_PATH in sys.path
        assert sys.path[0] == LIB_PATH
    assert LIB_PATH not in sys.path


def test_plugin_path():
    """Add plugin paths"""
    assert LIB_PATH not in plugins._plugin_paths
    plugins.add_plugin_path(LIB_PATH)
    assert LIB_PATH in plugins._plugin_paths


def test_plugin_loads():
    """Load a plugin"""
    name = 'fakeplugin'
    plugins.add_plugin_path(LIB_PATH)
    plugins.load_plugin(name)
    plugin = plugins.get_plugin(name)
    assert plugin is not None
    # No-op from testing point of view, but needed for code-branch
    # coverage
    plugins.load_plugin(name)
    # Invalid plugin
    plugins.load_plugin('doesnotexist')

if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
