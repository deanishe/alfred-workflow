#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-04
#
"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import unittest
from time import sleep

from util import create_info_plist, delete_info_plist

from workflow import Workflow
from workflow.background import is_running, run_in_background


class BackgroundTests(unittest.TestCase):

    def setUp(self):
        create_info_plist()

    def tearDown(self):
        delete_info_plist()

    def _pidfile(self, name):
        return Workflow().cachefile('{0}.pid'.format(name))

    def _write_pidfile(self, name, pid):
        pidfile = self._pidfile(name)
        with open(pidfile, 'wb') as file:
            file.write('{0}'.format(pid))

    def _delete_pidfile(self, name):
        pidfile = self._pidfile(name)
        if os.path.exists(pidfile):
            os.unlink(pidfile)

    def test_no_pidfile(self):
        """No pidfile"""
        self.assertFalse(is_running('boomstick'))

    def test_non_existent_process(self):
        """Non-existent process"""
        self._write_pidfile('test', 9999999)
        self.assertFalse(is_running('test'))
        self.assertFalse(os.path.exists(self._pidfile('test')))

    def test_existing_process(self):
        """Existing process"""
        self._write_pidfile('test', os.getpid())
        self.assertTrue(is_running('test'))
        self.assertTrue(os.path.exists(self._pidfile('test')))
        self._delete_pidfile('test')

    def test_run_in_background(self):
        """Run in background"""
        self.assertTrue(os.path.exists('info.plist'))
        cmd = ['sleep', '1']
        run_in_background('test', cmd)
        sleep(0.5)
        self.assertTrue(is_running('test'))
        self.assertTrue(os.path.exists(self._pidfile('test')))
        self.assertEqual(run_in_background('test', cmd), None)
        sleep(0.6)
        self.assertFalse(is_running('test'))
        self.assertFalse(os.path.exists(self._pidfile('test')))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
