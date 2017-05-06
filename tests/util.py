#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-17
#

"""
Stuff used in multiple tests.
"""

from __future__ import print_function, unicode_literals

from cStringIO import StringIO
import sys
import os
import shutil
import subprocess
import tempfile

INFO_PLIST_TEST = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'data/info.plist.alfred2')

INFO_PLIST_TEST3 = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'data/info.plist.alfred3')


INFO_PLIST_PATH = os.path.join(os.path.abspath(os.getcwdu()),
                               'info.plist')

VERSION_PATH = os.path.join(os.path.abspath(os.getcwdu()),
                            'version')

DEFAULT_SETTINGS = {
    'key1': 'value1',
    'key2': 'hübner',
    'mutable1': ['mutable', 'object'],
    'mutable2': {'mutable':  ['nested', 'object']},
}


class WorkflowMock(object):
    """Context manager that overrides funcs and variables for testing.

    c = WorkflowMock()
    with c:
        subprocess.call([arg1, arg2])
    c.cmd -> (arg1, arg2)

    """

    def __init__(self, argv=None, exit=True, call=True, stderr=False):
        """Context manager that overrides funcs and variables for testing.

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

        return self

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
    """Context manager to create and delete `version` file."""

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


class FakePrograms(object):
    """Context manager to inject fake programs into ``PATH``."""

    def __init__(self, *names, **names2codes):
        self.tempdir = None
        self.orig_path = None
        self.programs = {}
        for n in names:
            self.programs[n] = 1
        self.programs.update(names2codes)

    def __enter__(self):
        self.tempdir = tempfile.mkdtemp()
        for name, retcode in self.programs.items():
            path = os.path.join(self.tempdir, name)
            with open(path, 'wb') as fp:
                fp.write("#!/bin/bash\n\nexit {0}\n".format(retcode))
            os.chmod(path, 0700)

        # Add new programs to front of PATH
        self.orig_path = os.getenv('PATH')
        os.environ['PATH'] = '{0}:{1}'.format(self.tempdir, self.orig_path)

    def __exit__(self, *args):
        os.environ['PATH'] = self.orig_path
        try:
            shutil.rmtree(self.tempdir)
        except OSError:
            pass


class InfoPlist(object):
    """Context manager to create and delete ``info.plist``."""

    def __init__(self, path=None, dest_path=None, present=True):
        """Create new `InfoPlist` with paths."""
        self.path = path or INFO_PLIST_TEST
        self.dest_path = dest_path or INFO_PLIST_PATH
        # Whether or not Info.plist should be created or deleted
        self.present = present

    def __enter__(self):
        """Create or delete ``info.plist``."""
        if self.present:
            create_info_plist(self.path, self.dest_path)
        else:
            delete_info_plist(self.dest_path)

    def __exit__(self, *args):
        """Create or delete ``info.plist``."""
        if self.present:
            delete_info_plist(self.dest_path)


def create_info_plist(source=INFO_PLIST_TEST, dest=INFO_PLIST_PATH):
    """Symlink ``source`` to ``dest``."""
    if os.path.exists(source) and not os.path.exists(dest):
        os.symlink(source, dest)


def delete_info_plist(path=INFO_PLIST_PATH):
    """Delete ``path`` if it exists."""
    if os.path.exists(path) and os.path.islink(path):
        os.unlink(path)
