#!/usr/bin/env python
# encoding: utf-8

"""
test_workflow_lockfile.py

Created by deanishe@deanishe.net on 2015-08-15.
Copyright (c) 2015 deanishe@deanishe.net

MIT Licence. See http://opensource.org/licenses/MIT

"""

from __future__ import print_function, unicode_literals, absolute_import

import functools
import os
import shutil
import tempfile
import threading
import unittest

from workflow.workflow import Settings, LockFile, AcquisitionError


class LockFileTests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.protected_path = os.path.join(self.tempdir, 'testfile.txt')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def testSequentialAccess(self):
        """Lockfile: sequential access"""
        lock = LockFile(self.protected_path, 0.5)

        with lock:
            self.assertTrue(lock.locked)
            self.assertFalse(lock.acquire(False))
            self.assertRaises(AcquisitionError, lock.acquire, True)

        self.assertFalse(os.path.exists(lock.lockfile))

    def testConcurrentAccess(self):
        """Lockfile: Concurrent access"""
        lock = LockFile(self.protected_path, 0.5)

        def write_data(data, times=10):
            for i in range(times):
                with lock:
                    self.assertTrue(lock.locked)
                    with open(self.protected_path, 'a') as fp:
                        fp.write(data + '\n')
                        fp.flush()

                # time.sleep(0.05)

        threads = []
        for i in range(1, 5):
            t = threading.Thread(target=functools.partial(write_data,
                                 str(i) * 20))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.assertFalse(lock.locked)
        self.assertFalse(os.path.exists(lock.lockfile))

        # Check that every line consists of only one character
        with open(self.protected_path, 'rb') as fp:
            lines = [l.strip() for l in fp.readlines()]

        for line in lines:
            self.assertEquals(len(set(line)), 1)
        # print(lines)


class LockedSettingsTests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.settings_path = os.path.join(self.tempdir, 'settings.json')
        self.defaults = {'foo': 'bar'}
        Settings(self.settings_path, self.defaults)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def testConcurrentAccess(self):
        """Locked Settings: Concurrent access"""

        def save_data(key, value):
            settings = Settings(self.settings_path, self.defaults)
            settings[key] = value

        threads = []
        for i in range(1, 5):
            t = threading.Thread(target=functools.partial(save_data,
                                 'thread_{0}'.format(i),
                                 'value_{0}'.format(i)))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        settings = Settings(self.settings_path)
        print(settings)

if __name__ == '__main__':
    unittest.main()
