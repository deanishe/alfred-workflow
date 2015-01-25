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

from __future__ import print_function, unicode_literals, absolute_import

from cStringIO import StringIO
import sys
import os
import subprocess

import pytest

import workflow
import workflow.workflow
from workflow._env import WorkflowEnvironment

INFO_PLIST_TEST = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'data', 'info.plist.test')

INFO_PLIST_PATH = os.path.join(os.path.abspath(os.getcwdu()),
                               'info.plist')

VERSION_PATH = os.path.join(os.path.abspath(os.getcwdu()),
                            'version')


@pytest.fixture
def workflow_env(request, version=None, info_plist=True):
    ip_path = os.path.join(os.getcwdu(), 'info.plist')
    v_path = os.path.join(os.getcwdu(), 'version')
    v_delete = not os.path.exists(v_path)
    _env = workflow.env

    def tear_down():
        workflow.env = _env
        if v_delete and os.path.exists(v_path):
            os.unlink(v_path)
        if os.path.exists(ip_path) and os.path.islink(ip_path):
            os.unlink(ip_path)

    request.addfinalizer(tear_down)

    if version is not None:
        with open(v_path, 'wb') as fp:
            fp.write(str(version))

    if info_plist:
        if not os.path.exists(ip_path):
            os.symlink(INFO_PLIST_TEST, ip_path)

    workflow.env = WorkflowEnvironment()
    workflow.workflow.env = workflow.env


class WorkflowEnv(object):

    def __init__(self, version=None, info_plist=True):
        self.version = version
        self.info_plist = info_plist
        self.ip_path = os.path.join(INFO_PLIST_PATH)
        self.ip_backup = os.path.join(os.getcwdu(),
                                      'info.plist.{0}'.format(os.getpid()))

        self.v_path = os.path.join(os.getcwdu(), 'version')
        self.v_backup = os.path.join(os.getcwdu(),
                                     'version.{0}'.format(os.getpid()))

    def __enter__(self):
        # Move existing files
        if os.path.exists(self.ip_path):
            os.rename(self.ip_path, self.ip_backup)
        if os.path.exists(self.v_path):
            os.rename(self.v_path, self.v_backup)

        self._env = workflow.env

        if self.version is not None:
            with open(self.v_path, 'wb') as fp:
                fp.write(str(self.version))

        if self.info_plist:
            if not os.path.exists(self.ip_path):
                os.symlink(INFO_PLIST_TEST, self.ip_path)

        workflow.env = WorkflowEnvironment()
        workflow.workflow.env = workflow.env

    def __exit__(self, *args):
        workflow.env = self._env
        workflow.workflow.env = self._env
        if os.path.exists(self.v_backup):
            if os.path.exists(self.v_path):
                os.unlink(self.v_path)
            os.rename(self.v_backup, self.v_path)
        if os.path.exists(self.ip_backup):
            if os.path.exists(self.ip_path):
                os.unlink(self.ip_path)
            os.rename(self.ip_backup, self.ip_path)


class WorkflowMock(object):
    """Context manager that overrides funcs and variables for testing

    c = WorkflowMock()
    with c:
        subprocess.call([arg1, arg2])
    c.cmd -> (arg1, arg2)

    """

    def __init__(self, argv=None, exit=True, call=True, stderr=False):
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
        self.override_stderr = stderr
        self.argv_orig = None
        self.call_orig = None
        self.exit_orig = None
        self.stderr_orig = None
        self.cmd = ()
        self.args = []
        self.kwargs = {}
        self.stderr = ''

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

        if self.override_stderr:
            self.stderr_orig = sys.stderr
            sys.stderr = StringIO()

    def __exit__(self, *args):
        if self.call_orig:
            subprocess.call = self.call_orig

        if self.exit_orig:
            sys.exit = self.exit_orig

        if self.argv_orig:
            sys.argv = self.argv_orig[:]

        if self.stderr_orig:
            self.stderr = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = self.stderr_orig


class VersionFile(object):
    """Context manager to create and delete `version` file"""

    def __init__(self, version, path=None):

        self.version = version
        self.path = path or VERSION_PATH

    def __enter__(self):
        with open(self.path, 'wb') as fp:
            fp.write(self.version)
        print('version {0} in {1}'.format(self.version, self.path),
              file=sys.stderr)

    def __exit__(self, *args):
        if os.path.exists(self.path):
            os.unlink(self.path)


class InfoPlist(object):
    """Context manager to create and delete `info.plist` out of the way"""

    def __init__(self, path=None, dest_path=None, present=True):

        self.path = path or INFO_PLIST_TEST
        self.dest_path = dest_path or INFO_PLIST_PATH
        # Whether or not Info.plist should be created or deleted
        self.present = present

    def __enter__(self):
        if self.present:
            create_info_plist(self.path, self.dest_path)
        else:
            delete_info_plist(self.dest_path)

    def __exit__(self, *args):
        if self.present:
            delete_info_plist(self.dest_path)


def create_info_plist(source=INFO_PLIST_TEST, dest=INFO_PLIST_PATH):
    if os.path.exists(source) and not os.path.exists(dest):
        os.symlink(source, dest)


def delete_info_plist(path=INFO_PLIST_PATH):
    if os.path.exists(path) and os.path.islink(path):
        os.unlink(path)
