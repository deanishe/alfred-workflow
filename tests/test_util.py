#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-25
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import sys

from workflow import util

LIB_PATH = os.path.join(os.path.dirname(__file__), 'lib')


def test_syspath():
    """Manipulate `sys.path`"""
    assert LIB_PATH not in sys.path
    with util.syspath([LIB_PATH]):
        assert LIB_PATH in sys.path
        assert sys.path[0] == LIB_PATH
    assert LIB_PATH not in sys.path


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
