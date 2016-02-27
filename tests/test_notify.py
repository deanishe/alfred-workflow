#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-22
#

"""
test_notify.py

Unit tests for notify.py
"""

from __future__ import print_function

import hashlib
import logging
import os
import plistlib
import unittest
import shutil
import stat
import tempfile
from workflow import notify
from workflow.workflow import Workflow

from util import (
    FakePrograms,
    InfoPlist,
    WorkflowMock,
)

BUNDLE_ID = 'net.deanishe.alfred-workflow'
DATADIR = os.path.expanduser(
    '~/Library/Application Support/Alfred 2/'
    'Workflow Data/{0}'.format(BUNDLE_ID))
APP_PATH = os.path.join(DATADIR, 'Notify.app')
APPLET_PATH = os.path.join(APP_PATH, 'Contents/MacOS/applet')
ICON_PATH = os.path.join(APP_PATH, 'Contents/Resources/applet.icns')
INFO_PATH = os.path.join(APP_PATH, 'Contents/Info.plist')

# Alfred-Workflow icon (present in source distribution)
PNG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'icon.png')


class NotifyTests(unittest.TestCase):
    """Tests for :mod:`workflow.notify`."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        if os.path.exists(APP_PATH):
            shutil.rmtree(APP_PATH)

    def tearDown(self):
        if os.path.exists(APP_PATH):
            shutil.rmtree(APP_PATH)
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_log_wf(self):
        """Workflow and Logger objects correct"""
        with InfoPlist():
            wf = notify.wf()
            self.assert_(isinstance(wf, Workflow))
            # Always returns the same objects
            wf2 = notify.wf()
            self.assert_(wf is wf2)

            log = notify.log()
            self.assert_(isinstance(log, logging.Logger))
            log2 = notify.log()
            self.assert_(log is log2)

    def test_paths(self):
        """Module paths are correct"""
        with InfoPlist():
            self.assertEqual(DATADIR, notify.wf().datadir)
            self.assertEqual(APPLET_PATH, notify.notifier_program())
            self.assertEqual(ICON_PATH, notify.notifier_icon_path())

    def test_install(self):
        """Notify.app is installed correctly"""
        with InfoPlist():
            self.assertFalse(os.path.exists(APP_PATH))
            notify.install_notifier()
            for p in (APP_PATH, APPLET_PATH, ICON_PATH, INFO_PATH):
                self.assertTrue(os.path.exists(p))
            # Ensure applet is executable
            self.assert_(os.stat(APPLET_PATH).st_mode & stat.S_IXUSR)
            # Verify bundle ID was changed
            data = plistlib.readPlist(INFO_PATH)
            bid = data.get('CFBundleIdentifier')
            self.assertNotEqual(bid, BUNDLE_ID)
            self.assertTrue(bid.startswith(BUNDLE_ID))

    def test_sound(self):
        """Good sounds work, bad ones fail"""
        # Good values
        for s in ('basso', 'GLASS', 'Purr', 'tink'):
            sound = notify.validate_sound(s)
            self.assert_(sound is not None)
            self.assertEqual(sound, s.title())
        # Bad values
        for s in (None, 'SPOONS', 'The Hokey Cokey', ''):
            sound = notify.validate_sound(s)
            self.assert_(sound is None)

    def test_invalid_notifications(self):
        """Invalid notifications"""
        with InfoPlist():
            self.assertRaises(ValueError, notify.notify)
            # Is not installed yet
            self.assertFalse(os.path.exists(APP_PATH))
            self.assertTrue(notify.notify('Test Title', 'Test Message'))
            # A notification should appear now, but there's no way of
            # checking whether it worked
            self.assertTrue(os.path.exists(APP_PATH))

    def test_notifyapp_called(self):
        """Notify.app is called"""
        c = WorkflowMock()
        with InfoPlist():
            notify.install_notifier()
            with c:
                self.assertFalse(notify.notify('Test Title', 'Test Message'))
                self.assertEqual(c.cmd[0], APPLET_PATH)

    def test_iconutil_fails(self):
        """`iconutil` throws RuntimeError"""
        with InfoPlist():
            with FakePrograms('iconutil'):
                icns_path = os.path.join(self.tempdir, 'icon.icns')
                self.assertRaises(RuntimeError,
                                  notify.png_to_icns,
                                  PNG_PATH,
                                  icns_path)

    def test_sips_fails(self):
        """`sips` throws RuntimeError"""
        with InfoPlist():
            with FakePrograms('sips'):
                icon_path = os.path.join(self.tempdir, 'icon.png')
                self.assertRaises(RuntimeError,
                                  notify.convert_image,
                                  PNG_PATH, icon_path, 64)

    def test_image_conversion(self):
        """PNG to ICNS conversion"""
        with InfoPlist():
            self.assertFalse(os.path.exists(APP_PATH))
            notify.install_notifier()
            self.assertTrue(os.path.exists(APP_PATH))
            icns_path = os.path.join(self.tempdir, 'icon.icns')
            self.assertFalse(os.path.exists(icns_path))
            notify.png_to_icns(PNG_PATH, icns_path)
            self.assertTrue(os.path.exists(icns_path))
            with open(icns_path, 'rb') as fp:
                h1 = hashlib.md5(fp.read())
            with open(ICON_PATH, 'rb') as fp:
                h2 = hashlib.md5(fp.read())
            self.assertEqual(h1.digest(), h2.digest())
