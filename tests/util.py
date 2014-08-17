#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-17
#

"""
"""

from __future__ import print_function, unicode_literals

import os

INFO_PLIST_TEST = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'info.plist.test')


INFO_PLIST_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               'info.plist')


def create_info_plist():
    if not os.path.exists(INFO_PLIST_PATH):
        os.symlink(INFO_PLIST_TEST, INFO_PLIST_PATH)


def delete_info_plist():
    if os.path.exists(INFO_PLIST_PATH):
        os.unlink(INFO_PLIST_PATH)
