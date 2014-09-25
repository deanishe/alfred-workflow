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
Stuff used be multiple tests
"""

from __future__ import print_function, unicode_literals

import sys
import os
import subprocess

INFO_PLIST_TEST = os.path.join(os.path.abspath(os.getcwdu()),
                               'info.plist.test')


INFO_PLIST_PATH = os.path.join(os.path.dirname(os.path.abspath(os.getcwdu())),
                               'info.plist')


class WorkflowMock(object):
    """Context manager that overrides funcs and variables for testing

    c = WorkflowMock()
    with c:
        subprocess.call([arg1, arg2])
    c.cmd -> (arg1, arg2)

    """

    def __init__(self, argv=None, exit=True, call=True):
        """Context manager that overrides funcs and variables for testing

        :param argv: list of arguments to replace ``sys.argv`` with
        :type argv: list
        :param exit: Override ``sys.exit`` with noop?
        :param call: Override :func:`subprocess.call` and capture its
            arguments in :attr:`cmd`, :attr:`args` and :attr:`kwargs`?

        """

        self.argv = argv
        self.override_exit = exit
        self.override_call = call
        self.argv_orig = None
        self.call_orig = None
        self.exit_orig = None
        self.cmd = ()
        self.args = []
        self.kwargs = {}

    def _exit(self, status=0):
        return

    def _call(self, cmd, *args, **kwargs):
        self.cmd = cmd
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        if self.override_call:
            self.call_orig = subprocess.call
            subprocess.call = self._call

        if self.override_exit:
            self.exit_orig = sys.exit
            sys.exit = self._exit

        if self.argv:
            self.argv_orig = sys.argv[:]
            sys.argv = self.argv[:]

    def __exit__(self, *args):
        if self.call_orig:
            subprocess.call = self.call_orig

        if self.exit_orig:
            sys.exit = self.exit_orig

        if self.argv_orig:
            sys.argv = self.argv_orig[:]


def create_info_plist():
    if not os.path.exists(INFO_PLIST_PATH):
        os.symlink(INFO_PLIST_TEST, INFO_PLIST_PATH)


def delete_info_plist():
    if os.path.exists(INFO_PLIST_PATH):
        os.unlink(INFO_PLIST_PATH)
