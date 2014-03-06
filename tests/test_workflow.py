#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8
"""
test_workflow.py

Created by deanishe@deanishe.net on 2014-03-01.
Copyright (c) 2014 deanishe@deanishe.net.
"""

from __future__ import print_function, unicode_literals


import sys
import os
from StringIO import StringIO
import unittest
import json
import tempfile
import shutil
import logging
import time
from xml.etree import ElementTree as ET
from unicodedata import normalize

from workflow.workflow import (Workflow, Settings, PasswordNotFound,
                               KeychainError, MATCH_ALL, MATCH_ALLCHARS,
                               MATCH_ATOM, MATCH_CAPITALS, MATCH_STARTSWITH,
                               MATCH_SUBSTRING, MATCH_INITIALS_CONTAIN,
                               MATCH_INITIALS_STARTSWITH)

# info.plist settings
BUNDLE_ID = 'net.deanishe.alfred-workflow'
WORKFLOW_NAME = 'Alfred-Workflow Test'

DEFAULT_SETTINGS = {'key1': 'value1',
                    'key2': 'hübner'}


def setUp():
    pass


def tearDown():
    pass


class WorkflowTests(unittest.TestCase):

    def setUp(self):
        self.libs = [os.path.join(os.path.dirname(__file__), 'lib')]
        self.wf = Workflow(libraries=self.libs)
        self.account = 'this-is-my-test-account'
        self.password = 'this-is-my-safe-password'
        self.password2 = 'this-is-my-other-safe-password'
        self.search_items = [
            ('Test Item One', MATCH_STARTSWITH),
            ('test item two', MATCH_STARTSWITH),
            ('TwoExtraSpecialTests', MATCH_CAPITALS),
            ('this-is-a-test', MATCH_ATOM),
            ('the extra special trials', MATCH_INITIALS_STARTSWITH),
            ('not the extra special trials', MATCH_INITIALS_CONTAIN),
            ('intestinal fortitude', MATCH_SUBSTRING),
            ('the splits', MATCH_ALLCHARS),
            ('nomatch', 0),
        ]

    def tearDown(self):
        self.wf.clear_cache()
        self.wf.clear_settings()
        try:
            self.wf.delete_password(self.account)
        except PasswordNotFound:
            pass
        for dirpath in (self.wf.cachedir, self.wf.datadir):
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)

    def test_item_creation(self):
        """XML generation"""
        self.wf.add_item('title', 'subtitle', 'arg',
                         autocomplete='autocomplete',
                         valid=True, uid='uid', icon='icon.png',
                         icontype='fileicon',
                         type='file')
        stdout = sys.stdout
        sio = StringIO()
        sys.stdout = sio
        self.wf.send_feedback()
        sys.stdout = stdout
        output = sio.getvalue()
        sio.close()
        # pprint(output)
        root = ET.fromstring(output)
        item = list(root)[0]
        self.assertEquals(item.attrib['uid'], 'uid')
        self.assertEquals(item.attrib['autocomplete'], 'autocomplete')
        self.assertEquals(item.attrib['valid'], 'yes')
        self.assertEquals(item.attrib['uid'], 'uid')
        title, subtitle, arg, icon = list(item)
        self.assertEquals(title.text, 'title')
        self.assertEquals(title.tag, 'title')
        self.assertEquals(subtitle.text, 'subtitle')
        self.assertEquals(subtitle.tag, 'subtitle')
        self.assertEquals(arg.text, 'arg')
        self.assertEquals(arg.tag, 'arg')
        self.assertEquals(icon.text, 'icon.png')
        self.assertEquals(icon.tag, 'icon')
        self.assertEquals(icon.attrib['type'], 'fileicon')

    def test_item_creation_no_optionals(self):
        """XML generation (no optionals)"""
        self.wf.add_item('title',
                         valid=False)
        stdout = sys.stdout
        sio = StringIO()
        sys.stdout = sio
        self.wf.send_feedback()
        sys.stdout = stdout
        output = sio.getvalue()
        sio.close()
        # pprint(output)
        root = ET.fromstring(output)
        item = list(root)[0]
        for key in ['uid', 'arg', 'autocomplete']:
            self.assertFalse(key in item.attrib)
        self.assertEquals(item.attrib['valid'], 'no')
        title, subtitle = list(item)
        self.assertEquals(title.text, 'title')
        self.assertEquals(title.tag, 'title')
        self.assertEquals(subtitle.text, None)
        tags = [elem.tag for elem in list(item)]
        for tag in ['icon', 'arg']:
            self.assert_(tag not in tags)

    def test_additional_libs(self):
        """Additional libraries"""
        for path in self.libs:
            self.assert_(path in sys.path)
        self.assertEquals(sys.path[0:len(self.libs)], self.libs)
        import youcanimportme

    def test_info_plist(self):
        """info.plist"""
        self.assertEquals(self.wf.name, WORKFLOW_NAME)
        self.assertEquals(self.wf.bundleid, BUNDLE_ID)

    def test_args(self):
        """ARGV"""
        args = ['arg1', 'arg2', 'füntíme']
        oargs = sys.argv[:]
        sys.argv = [oargs[0]] + [s.encode('utf-8') for s in args]
        wf = Workflow()
        try:
            self.assertEquals(wf.args, args)
        finally:
            sys.argv = oargs[:]

    def test_arg_normalisation(self):
        """ARGV normalisation"""
        def nfdme(s):
            return normalize('NFD', s)
        args = map(nfdme, ['arg1', 'arg2', 'füntíme'])
        oargs = sys.argv[:]
        sys.argv = [oargs[0]] + [s.encode('utf-8') for s in args]
        wf = Workflow(normalization='NFD')
        try:
            self.assertEquals(wf.args, args)
        finally:
            sys.argv = oargs[:]

    def test_magic_args(self):
        """Magic args"""
        # cache original sys.argv
        oargs = sys.argv[:]

        # # openlog
        # sys.argv = [oargs[0]] + [b'workflow:openlog']
        # try:
        #     wf = Workflow()
        #     wf.logger.debug('This is a test message')  # ensure log file exists
        #     with self.assertRaises(SystemExit):
        #         wf.args
        # finally:
        #     sys.argv = oargs[:]

        # delsettings
        sys.argv = [oargs[0]] + [b'workflow:delsettings']
        try:
            wf = Workflow(default_settings={'arg1': 'value1'})
            self.assertEquals(wf.settings['arg1'], 'value1')
            self.assertTrue(os.path.exists(wf.settings_path))
            with self.assertRaises(SystemExit):
                wf.args
            self.assertFalse(os.path.exists(wf.settings_path))
        finally:
            sys.argv = oargs[:]

        # delcache
        sys.argv = [oargs[0]] + [b'workflow:delcache']

        def somedata():
            return {'arg1': 'value1'}

        try:
            wf = Workflow()
            cachepath = wf.cachefile('somedir')
            os.makedirs(cachepath)
            wf.cached_data('test', somedata)
            self.assertTrue(os.path.exists(wf.cachefile('test.cache')))
            with self.assertRaises(SystemExit):
                wf.args
            self.assertFalse(os.path.exists(wf.cachefile('test.cache')))
        finally:
            sys.argv = oargs[:]

    def test_logger(self):
        """Logger"""
        self.assert_(isinstance(self.wf.logger, logging.Logger))
        logger = logging.Logger('')
        self.wf.logger = logger
        self.assertEquals(self.wf.logger, logger)

    def test_cached_data(self):
        """Cached data stored"""
        data = {'key1': 'value1'}
        d = self.wf.cached_data('test', lambda: data, max_age=10)
        self.assertEquals(data, d)

    def test_cached_data_callback(self):
        """Cached data callback"""
        called = {'called': False}
        data = [1, 2, 3]

        def getdata():
            called['called'] = True
            return data

        d = self.wf.cached_data('test', getdata, max_age=10)
        self.assertEquals(d, data)
        self.assertTrue(called['called'])

    def test_cache_expires(self):
        """Cached data expires"""
        data = ('hello', 'goodbye')
        called = {'called': False}

        def getdata():
            called['called'] = True
            return data

        d = self.wf.cached_data('test', getdata, max_age=1)
        self.assertEquals(d, data)
        self.assertTrue(called['called'])
        # should be loaded from cache
        called['called'] = False
        d2 = self.wf.cached_data('test', getdata, max_age=1)
        self.assertEquals(d2, data)
        self.assertFalse(called['called'])
        # cache has expired
        time.sleep(1)
        # should be loaded from cache (no expiry)
        d3 = self.wf.cached_data('test', getdata, max_age=0)
        self.assertEquals(d3, data)
        self.assertFalse(called['called'])
        # should hit data func (cached data older than 1 sec)
        d4 = self.wf.cached_data('test', getdata, max_age=1)
        self.assertEquals(d4, data)
        self.assertTrue(called['called'])

    def test_cache_fresh(self):
        """Cached data is fresh"""
        data = 'This is my data'
        d = self.wf.cached_data('test', lambda: data, max_age=1)
        self.assertEquals(d, data)
        self.assertTrue(self.wf.cached_data_fresh('test', max_age=10))

    def test_keychain(self):
        """Save/get/delete password"""
        self.assertRaises(PasswordNotFound,
                          self.wf.delete_password, self.account)
        self.assertRaises(PasswordNotFound, self.wf.get_password, self.account)
        self.wf.save_password(self.account, self.password)
        self.assertEquals(self.wf.get_password(self.account), self.password)
        self.assertEquals(self.wf.get_password(self.account, BUNDLE_ID),
                          self.password)
        # try to set same password
        self.wf.save_password(self.account, self.password)
        self.assertEquals(self.wf.get_password(self.account), self.password)
        # try to set different password
        self.wf.save_password(self.account, self.password2)
        self.assertEquals(self.wf.get_password(self.account), self.password2)
        # bad call to _call_security
        with self.assertRaises(KeychainError):
            self.wf._call_security('pants', BUNDLE_ID, self.account)

    def test_run_fails(self):
        """Run fails"""
        def cb(wf):
            self.assertEquals(wf, self.wf)
            raise ValueError('Have an error')
        self.wf.name  # cause info.plist to be parsed
        ret = self.wf.run(cb)
        self.assertEquals(ret, 1)
        # named after bundleid
        self.wf = Workflow()
        self.wf.bundleid
        ret = self.wf.run(cb)
        self.assertEquals(ret, 1)

    def test_run_okay(self):
        """Run okay"""
        def cb(wf):
            self.assertEquals(wf, self.wf)
        ret = self.wf.run(cb)
        self.assertEquals(ret, 0)

    def test_filter_all_rules(self):
        """Filter: all rules"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True)
        self.assertEquals(len(results), 8)
        # now with scores, rules
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 include_score=True)
        self.assertEquals(len(results), 8)
        for item, score, rule in results:
            self.wf.logger.debug('{} : {}'.format(item, score))
            for value, r in self.search_items:
                if value == item[0]:
                    self.assertEquals(rule, r)
        # self.assertTrue(False)

    def test_filter_no_caps(self):
        """Filter: no caps"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True,
                                 match_on=MATCH_ALL ^ MATCH_CAPITALS,
                                 include_score=True)
        self._print_results(results)
        for item, score, rule in results:
            self.assertNotEqual(rule, MATCH_CAPITALS)
        # self.assertEquals(len(results), 7)

    def test_filter_only_caps(self):
        """Filter: only caps"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True,
                                 match_on=MATCH_CAPITALS,
                                 include_score=True)
        self._print_results(results)
        self.assertEqual(len(results), 1)

    def test_filter_max_results(self):
        """Filter: max results"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True, max_results=4)
        self.assertEquals(len(results), 4)

    def test_filter_min_score(self):
        """Filter: min score"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True, min_score=90,
                                 include_score=True)
        self.assertEquals(len(results), 6)

    def test_icons(self):
        """Icons"""
        import workflow
        for name in dir(workflow):
            if name.startswith('ICON_'):
                path = getattr(workflow, name)
                print(name, path)
                self.assert_(os.path.exists(path))

    def _print_results(self, results):
        """Print results of Workflow.filter"""
        for item, score, rule in results:
            print('{0} (rule {1}) : {2}'.format(item[0], rule, score))


class SettingsTests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.tempdir, 'settings.json')
        with open(self.settings_file, 'wb') as file:
            json.dump(DEFAULT_SETTINGS, file)

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_defaults(self):
        """Default settings"""
        if os.path.exists(self.settings_file):
            os.unlink(self.settings_file)
        s = Settings(self.settings_file, {'key1': 'value2'})
        self.assertEquals(s['key1'], 'value2')

    def test_load_settings(self):
        """Load saved settings"""
        s = Settings(self.settings_file, {'key1': 'value2'})
        for key in DEFAULT_SETTINGS:
            self.assertEquals(DEFAULT_SETTINGS[key], s[key])

    def test_save_settings(self):
        """Settings saved"""
        s = Settings(self.settings_file)
        self.assertEquals(s['key1'], DEFAULT_SETTINGS['key1'])
        s['key1'] = 'spoons!'
        s2 = Settings(self.settings_file)
        self.assertEquals(s['key1'], s2['key1'])

    def test_dict_methods(self):
        """Settings dict methods"""
        other = {'key1': 'spoons!'}
        s = Settings(self.settings_file)
        self.assertEquals(s['key1'], DEFAULT_SETTINGS['key1'])
        s.update(other)
        s.setdefault('alist', [])
        s2 = Settings(self.settings_file)
        self.assertEquals(s['key1'], s2['key1'])
        self.assertEquals(s['key1'], 'spoons!')
        self.assertEquals(s2['alist'], [])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
