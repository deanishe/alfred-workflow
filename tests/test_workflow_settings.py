#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-24
#

"""Unit tests for Workflow.settings API."""



import json
import os
import shutil
import time
import tempfile
import unittest

from workflow.workflow import Settings

from tests.util import DEFAULT_SETTINGS


class SettingsTests(unittest.TestCase):
    """Test suite for `workflow.workflow.Settings`."""

    def setUp(self):
        """Initialise unit test environment."""
        self.tempdir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.tempdir, 'settings.json')
        with open(self.settings_file, 'w') as file_obj:
            json.dump(DEFAULT_SETTINGS, file_obj)

    def tearDown(self):
        """Reset unit test environment."""
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_defaults(self):
        """Default settings"""
        if os.path.exists(self.settings_file):
            os.unlink(self.settings_file)
        s = Settings(self.settings_file, {'key1': 'value2'})
        self.assertEqual(s['key1'], 'value2')

    def test_load_settings(self):
        """Load saved settings"""
        s = Settings(self.settings_file, {'key1': 'value2'})
        for key in DEFAULT_SETTINGS:
            self.assertEqual(DEFAULT_SETTINGS[key], s[key])

    def test_save_settings(self):
        """Settings saved"""
        s = Settings(self.settings_file)
        self.assertEqual(s['key1'], DEFAULT_SETTINGS['key1'])
        s['key1'] = 'spoons!'
        s2 = Settings(self.settings_file)
        self.assertEqual(s['key1'], s2['key1'])

    def test_delete_settings(self):
        """Settings deleted"""
        s = Settings(self.settings_file)
        self.assertEqual(s['key1'], DEFAULT_SETTINGS['key1'])
        del s['key1']
        s2 = Settings(self.settings_file)
        self.assertEqual(s2.get('key1'), None)

    def test_dict_methods(self):
        """Settings dict methods"""
        other = {'key1': 'spoons!'}
        s = Settings(self.settings_file)
        self.assertEqual(s['key1'], DEFAULT_SETTINGS['key1'])
        s.update(other)
        s.setdefault('alist', [])
        s2 = Settings(self.settings_file)
        self.assertEqual(s['key1'], s2['key1'])
        self.assertEqual(s['key1'], 'spoons!')
        self.assertEqual(s2['alist'], [])

    def test_settings_not_rewritten(self):
        """Settings not rewritten for same value"""
        s = Settings(self.settings_file)
        mt = os.path.getmtime(self.settings_file)
        time.sleep(0.1)  # wait long enough to register changes in `time.time()`
        now = time.time()
        for k, v in list(DEFAULT_SETTINGS.items()):
            s[k] = v
        self.assertTrue(os.path.getmtime(self.settings_file) == mt)
        s['finished_at'] = now
        s2 = Settings(self.settings_file)
        self.assertEqual(s['finished_at'], s2['finished_at'])
        self.assertTrue(os.path.getmtime(self.settings_file) > mt)

    def test_mutable_objects_updated(self):
        """Updated mutable objects cause save"""
        s = Settings(self.settings_file)
        mt1 = os.path.getmtime(self.settings_file)
        time.sleep(0.1)
        seq = s['mutable1']
        seq.append('another string')
        s['mutable1'] = seq
        mt2 = os.path.getmtime(self.settings_file)
        self.assertTrue(mt2 > mt1)
        s2 = Settings(self.settings_file)
        self.assertTrue('another string' in s2['mutable1'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
