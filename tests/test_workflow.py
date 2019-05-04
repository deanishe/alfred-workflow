#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-01
#

"""Unit tests for :mod:`workflow.Workflow`."""

from __future__ import print_function, unicode_literals

import json
import logging
import os
import shutil
from StringIO import StringIO
import sys
import time
import unittest

from unicodedata import normalize

from util import (
    VersionFile,
    InfoPlist,
    INFO_PLIST_PATH,
    create_info_plist,
    delete_info_plist,
)

from workflow.workflow import (Workflow, PasswordNotFound,
                               KeychainError, MATCH_ALL, MATCH_ALLCHARS,
                               MATCH_ATOM, MATCH_CAPITALS, MATCH_STARTSWITH,
                               MATCH_SUBSTRING, MATCH_INITIALS_CONTAIN,
                               MATCH_INITIALS_STARTSWITH,
                               manager)

from workflow.update import Version

# info.plist settings
BUNDLE_ID = 'net.deanishe.alfred-workflow'
WORKFLOW_NAME = 'Alfred-Workflow Test'


class WorkflowTests(unittest.TestCase):
    """Test suite for workflow.workflow.Workflow."""

    def setUp(self):
        self.libs = [os.path.join(os.path.dirname(__file__), b'lib')]
        self.account = 'this-is-my-test-account'
        self.password = 'this-is-my-safe-password'
        self.password2 = 'this-is-my-other-safe-password'
        self.password3 = 'this-pässwörd-is\\"non-ASCII"'
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

        self.search_items_diacritics = [
            # search key, query
            ('Änderungen vorbehalten', 'av'),
            ('Änderungen', 'anderungen'),
            ('überwiegend bewolkt', 'ub'),
            ('überwiegend', 'uberwiegend'),
            ('Öffnungszeiten an Feiertagen', 'offnungszeiten'),
            ('Öffnungszeiten an Feiertagen', 'oaf'),
            ('Fußpilz', 'fuss'),
            ('salé', 'sale')
        ]

        self.punctuation_data = [
            ('"test"', '"test"'),
            ('„wat denn?“', '"wat denn?"'),
            ('‚wie dat denn?‘', "'wie dat denn?'"),
            ('“test”', '"test"'),
            ('and—why—not', 'and-why-not'),
            ('10–20', '10-20'),
            ('Shady’s back', "Shady's back"),
        ]

        self.env_data = {
            'alfred_debug': b'1',
            'alfred_preferences':
            os.path.expanduser(b'~/Dropbox/Alfred/Alfred.alfredpreferences'),
            'alfred_preferences_localhash':
            b'adbd4f66bc3ae8493832af61a41ee609b20d8705',
            'alfred_theme': b'alfred.theme.yosemite',
            'alfred_theme_background': b'rgba(255,255,255,0.98)',
            'alfred_theme_subtext': b'3',
            'alfred_version': b'2.4',
            'alfred_version_build': b'277',
            'alfred_workflow_bundleid': str(BUNDLE_ID),
            'alfred_workflow_cache':
            os.path.expanduser(b'~/Library/Caches/com.runningwithcrayons.'
                               b'Alfred-2/Workflow Data/{0}'.format(BUNDLE_ID)),
            'alfred_workflow_data':
            os.path.expanduser(b'~/Library/Application Support/Alfred 2/'
                               b'Workflow Data/{0}'.format(BUNDLE_ID)),
            'alfred_workflow_name': b'Alfred-Workflow Test',
            'alfred_workflow_uid':
            b'user.workflow.B0AC54EC-601C-479A-9428-01F9FD732959',
        }

        self._setup_env()
        create_info_plist()

        self.wf = Workflow(libraries=self.libs)

    def tearDown(self):
        create_info_plist()
        self.wf.reset()
        try:
            self.wf.delete_password(self.account)
        except PasswordNotFound:
            pass

        for dirpath in (self.wf.cachedir, self.wf.datadir):
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)

        self._teardown_env()
        delete_info_plist()

    ####################################################################
    # Environment
    ####################################################################

    def test_additional_libs(self):
        """Additional libraries"""
        for path in self.libs:
            self.assert_(path in sys.path)
        self.assertEqual(sys.path[0:len(self.libs)], self.libs)
        import youcanimportme
        youcanimportme.noop()

    def test_info_plist(self):
        """info.plist"""
        self._teardown_env()
        self.assertEqual(self.wf.name, WORKFLOW_NAME)
        self.assertEqual(self.wf.bundleid, BUNDLE_ID)

    def test_info_plist_missing(self):
        """Info.plist missing"""
        # delete_info_plist()
        self._teardown_env()
        with InfoPlist(present=False):
            wf = Workflow()
            self.assertFalse(os.path.exists(INFO_PLIST_PATH))
            # self.assertRaises(IOError, lambda wf: wf.info, wf)
            self.assertRaises(IOError, lambda: wf.workflowdir)
        # try:
        #     self.assertRaises(IOError, Workflow)
        # finally:
        #     create_info_plist()

    def test_alfred_env_vars(self):
        """Alfred environmental variables"""
        for key in self.env_data:
            value = self.env_data[key]
            key = key.replace('alfred_', '')
            if key in ('debug', 'version_build', 'theme_subtext'):
                self.assertEqual(int(value), self.wf.alfred_env[key])
            else:
                self.assertEqual(unicode(value), self.wf.alfred_env[key])
                self.assertTrue(isinstance(self.wf.alfred_env[key], unicode))

        self.assertEqual(self.wf.datadir,
                         self.env_data['alfred_workflow_data'])
        self.assertEqual(self.wf.cachedir,
                         self.env_data['alfred_workflow_cache'])
        self.assertEqual(self.wf.bundleid,
                         self.env_data['alfred_workflow_bundleid'])
        self.assertEqual(self.wf.name,
                         self.env_data['alfred_workflow_name'])

    def test_alfred_debugger(self):
        """Alfred debugger status"""
        wf = Workflow()
        self.assertTrue(wf.debugging)  # Alfred's debugger is open
        self.assertEqual(wf.logger.getEffectiveLevel(), logging.DEBUG)

        # With debugger off
        self._teardown_env()
        data = self.env_data.copy()
        del data['alfred_debug']
        self._setup_env(data)
        wf = Workflow()
        self.assertFalse(wf.debugging)  # Alfred's debugger is closed
        self.assertEqual(wf.logger.getEffectiveLevel(), logging.INFO)

    ####################################################################
    # ARGV
    ####################################################################

    def test_args(self):
        """ARGV"""
        args = ['arg1', 'arg2', 'füntíme']
        oargs = sys.argv[:]
        sys.argv = [oargs[0]] + [s.encode('utf-8') for s in args]
        wf = Workflow()
        try:
            self.assertEqual(wf.args, args)
        finally:
            sys.argv = oargs[:]

    def test_arg_normalisation(self):
        """ARGV normalisation"""
        def nfdme(s):
            """NFD-normalise string"""
            return normalize('NFD', s)

        args = [nfdme(s) for s in ['arg1', 'arg2', 'füntíme']]
        oargs = sys.argv[:]
        sys.argv = [oargs[0]] + [s.encode('utf-8') for s in args]

        wf = Workflow(normalization='NFD')
        try:
            self.assertEqual(wf.args, args)
        finally:
            sys.argv = oargs[:]

    def test_magic_args(self):
        """Magic args"""
        # cache original sys.argv
        oargs = sys.argv[:]

        # delsettings
        sys.argv = [oargs[0]] + [b'workflow:delsettings']
        try:
            wf = Workflow(default_settings={'arg1': 'value1'})
            self.assertEqual(wf.settings['arg1'], 'value1')
            self.assertTrue(os.path.exists(wf.settings_path))
            self.assertRaises(SystemExit, lambda wf: wf.args, wf)
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
            self.assertTrue(os.path.exists(wf.cachefile('test.cpickle')))
            self.assertRaises(SystemExit, lambda wf: wf.args, wf)
            self.assertFalse(os.path.exists(wf.cachefile('test.cpickle')))
        finally:
            sys.argv = oargs[:]

    def test_logger(self):
        """Logger"""
        self.assert_(isinstance(self.wf.logger, logging.Logger))
        logger = logging.Logger('')
        self.wf.logger = logger
        self.assertEqual(self.wf.logger, logger)

    ####################################################################
    # Cached data
    ####################################################################

    def test_cached_data(self):
        """Cached data stored"""
        data = {'key1': 'value1'}
        d = self.wf.cached_data('test', lambda: data, max_age=10)
        self.assertEqual(data, d)

    def test_cached_data_deleted(self):
        """Cached data deleted"""
        data = {'key1': 'value1'}
        d = self.wf.cached_data('test', lambda: data, max_age=10)
        self.assertEqual(data, d)
        ret = self.wf.cache_data('test', None)
        self.assertEquals(ret, None)
        self.assertFalse(os.path.exists(self.wf.cachefile('test.cpickle')))
        # Test alternate code path for non-existent file
        self.assertEqual(self.wf.cache_data('test', None), None)

    def test_delete_all_cache_file(self):
        """Cached data are all deleted"""
        data = {'key1': 'value1'}
        test_file1 = 'test1.cpickle'
        test_file2 = 'test2.cpickle'

        self.wf.cached_data('test1', lambda: data, max_age=10)
        self.wf.cached_data('test2', lambda: data, max_age=10)
        self.assertTrue(os.path.exists(self.wf.cachefile(test_file1)))
        self.assertTrue(os.path.exists(self.wf.cachefile(test_file2)))
        self.wf.clear_cache()
        self.assertFalse(os.path.exists(self.wf.cachefile(test_file1)))
        self.assertFalse(os.path.exists(self.wf.cachefile(test_file2)))

    def test_delete_all_cache_file_with_filter_func(self):
        """Only part of cached data are deleted"""
        data = {'key1': 'value1'}
        test_file1 = 'test1.cpickle'
        test_file2 = 'test2.cpickle'

        def filter_func(file):
            if file == test_file1:
                return True
            else:
                return False

        self.wf.cached_data('test1', lambda: data, max_age=10)
        self.wf.cached_data('test2', lambda: data, max_age=10)
        self.assertTrue(os.path.exists(self.wf.cachefile(test_file1)))
        self.assertTrue(os.path.exists(self.wf.cachefile(test_file2)))
        self.wf.clear_cache(filter_func)
        self.assertFalse(os.path.exists(self.wf.cachefile(test_file1)))
        self.assertTrue(os.path.exists(self.wf.cachefile(test_file2)))
        self.wf.clear_cache()
        self.assertFalse(os.path.exists(self.wf.cachefile(test_file2)))

    def test_cached_data_callback(self):
        """Cached data callback"""
        called = {'called': False}
        data = [1, 2, 3]

        def getdata():
            called['called'] = True
            return data

        d = self.wf.cached_data('test', getdata, max_age=10)
        self.assertEqual(d, data)
        self.assertTrue(called['called'])

    def test_cached_data_no_callback(self):
        """Cached data no callback"""
        d = self.wf.cached_data('nonexistent', None)
        self.assertEqual(d, None)

    def test_cache_expires(self):
        """Cached data expires"""
        data = ('hello', 'goodbye')
        called = {'called': False}

        def getdata():
            called['called'] = True
            return data

        d = self.wf.cached_data('test', getdata, max_age=1)
        self.assertEqual(d, data)
        self.assertTrue(called['called'])
        # should be loaded from cache
        called['called'] = False
        d2 = self.wf.cached_data('test', getdata, max_age=1)
        self.assertEqual(d2, data)
        self.assertFalse(called['called'])
        # cache has expired
        time.sleep(1)
        # should be loaded from cache (no expiry)
        d3 = self.wf.cached_data('test', getdata, max_age=0)
        self.assertEqual(d3, data)
        self.assertFalse(called['called'])
        # should hit data func (cached data older than 1 sec)
        d4 = self.wf.cached_data('test', getdata, max_age=1)
        self.assertEqual(d4, data)
        self.assertTrue(called['called'])

    def test_cache_fresh(self):
        """Cached data is fresh"""
        data = 'This is my data'
        d = self.wf.cached_data('test', lambda: data, max_age=1)
        self.assertEqual(d, data)
        self.assertTrue(self.wf.cached_data_fresh('test', max_age=10))

    def test_cache_fresh_non_existent(self):
        """Non-existent cache data is not fresh"""
        self.assertEqual(self.wf.cached_data_fresh('popsicle', max_age=10000),
                         False)

    ####################################################################
    # Serialisation
    ####################################################################

    def test_cache_serializer(self):
        """Cache serializer"""
        self.assertEqual(self.wf.cache_serializer, 'cpickle')

        def set_serializer(wf, serializer):
            wf.cache_serializer = serializer

        self.assertRaises(ValueError, set_serializer, self.wf, 'non-existent')
        self.assertEqual(self.wf.cache_serializer, 'cpickle')
        self.wf.cache_serializer = 'pickle'
        self.assertEqual(self.wf.cache_serializer, 'pickle')

    def test_alternative_cache_serializer(self):
        """Alternative cache serializer"""
        data = {'key1': 'value1'}
        self.assertEqual(self.wf.cache_serializer, 'cpickle')
        self.wf.cache_data('test', data)
        self.assertTrue(os.path.exists(self.wf.cachefile('test.cpickle')))
        self.assertEqual(data, self.wf.cached_data('test'))

        self.wf.cache_serializer = 'pickle'
        self.assertEqual(None, self.wf.cached_data('test'))
        self.wf.cache_data('test', data)
        self.assertTrue(os.path.exists(self.wf.cachefile('test.pickle')))
        self.assertEqual(data, self.wf.cached_data('test'))

        self.wf.cache_serializer = 'json'
        self.assertEqual(None, self.wf.cached_data('test'))
        self.wf.cache_data('test', data)
        self.assertTrue(os.path.exists(self.wf.cachefile('test.json')))
        self.assertEqual(data, self.wf.cached_data('test'))

    def test_custom_cache_serializer(self):
        """Custom cache serializer"""
        data = {'key1': 'value1'}

        class MySerializer(object):
            """Simple serializer"""
            @classmethod
            def load(self, file_obj):
                return json.load(file_obj)

            @classmethod
            def dump(self, obj, file_obj):
                return json.dump(obj, file_obj, indent=2)

        manager.register('spoons', MySerializer)
        try:
            self.assertFalse(os.path.exists(self.wf.cachefile('test.spoons')))
            self.wf.cache_serializer = 'spoons'
            self.wf.cache_data('test', data)
            self.assertTrue(os.path.exists(self.wf.cachefile('test.spoons')))
            self.assertEqual(data, self.wf.cached_data('test'))
        finally:
            manager.unregister('spoons')

    def test_data_serializer(self):
        """Data serializer"""
        self.assertEqual(self.wf.data_serializer, 'cpickle')

        def set_serializer(wf, serializer):
            wf.data_serializer = serializer

        self.assertRaises(ValueError, set_serializer, self.wf, 'non-existent')
        self.assertEqual(self.wf.data_serializer, 'cpickle')
        self.wf.data_serializer = 'pickle'
        self.assertEqual(self.wf.data_serializer, 'pickle')

    def test_alternative_data_serializer(self):
        """Alternative data serializer"""
        data = {'key7': 'value7'}

        self.assertEqual(self.wf.data_serializer, 'cpickle')
        self.wf.store_data('test', data)
        for path in self._stored_data_paths('test', 'cpickle'):
            self.assertTrue(os.path.exists(path))
        self.assertEqual(data, self.wf.stored_data('test'))

        self.wf.data_serializer = 'pickle'
        self.assertEqual(data, self.wf.stored_data('test'))
        self.wf.store_data('test', data)
        for path in self._stored_data_paths('test', 'pickle'):
            self.assertTrue(os.path.exists(path))
        self.assertEqual(data, self.wf.stored_data('test'))

        self.wf.data_serializer = 'json'
        self.assertEqual(data, self.wf.stored_data('test'))
        self.wf.store_data('test', data)
        for path in self._stored_data_paths('test', 'json'):
            self.assertTrue(os.path.exists(path))
        self.assertEqual(data, self.wf.stored_data('test'))

    def test_non_existent_stored_data(self):
        """Non-existent stored data"""
        self.assertTrue(self.wf.stored_data('banjo magic') is None)

    def test_borked_stored_data(self):
        """Borked stored data"""
        data = {'key7': 'value7'}

        self.wf.store_data('test', data)
        metadata, datapath = self._stored_data_paths('test', 'cpickle')
        os.unlink(metadata)
        self.assertEqual(self.wf.stored_data('test'), None)

        self.wf.store_data('test', data)
        metadata, datapath = self._stored_data_paths('test', 'cpickle')
        os.unlink(datapath)
        self.assertTrue(self.wf.stored_data('test') is None)

        self.wf.store_data('test', data)
        metadata, datapath = self._stored_data_paths('test', 'cpickle')
        with open(metadata, 'wb') as file_obj:
            file_obj.write('bangers and mash')
            self.wf.logger.debug('Changed format to `bangers and mash`')
        self.assertRaises(ValueError, self.wf.stored_data, 'test')

    def test_reject_settings(self):
        """Disallow settings.json"""
        data = {'key7': 'value7'}

        self.wf.data_serializer = 'json'

        self.assertRaises(ValueError, self.wf.store_data, 'settings', data)

    def test_invalid_data_serializer(self):
        """Invalid data serializer"""
        data = {'key7': 'value7'}

        self.assertRaises(ValueError, self.wf.store_data, 'test', data,
                          'spong')

    ####################################################################
    # Data deletion
    ####################################################################

    def test_delete_stored_data(self):
        """Delete stored data"""
        data = {'key7': 'value7'}

        paths = self._stored_data_paths('test', 'cpickle')

        self.wf.store_data('test', data)
        self.assertEqual(data, self.wf.stored_data('test'))
        self.wf.store_data('test', None)
        self.assertEqual(None, self.wf.stored_data('test'))

        for p in paths:
            self.assertFalse(os.path.exists(p))

    def test_delete_all_stored_data_file(self):
        """Stored data are all deleted"""
        data = {'key1': 'value1'}
        test_file1 = 'test1.cpickle'
        test_file2 = 'test2.cpickle'

        self.wf.store_data('test1', data)
        self.wf.store_data('test2', data)
        self.assertTrue(os.path.exists(self.wf.datafile(test_file1)))
        self.assertTrue(os.path.exists(self.wf.datafile(test_file2)))
        self.wf.clear_data()
        self.assertFalse(os.path.exists(self.wf.datafile(test_file1)))
        self.assertFalse(os.path.exists(self.wf.datafile(test_file2)))

    def test_delete_all_data_file_with_filter_func(self):
        """Only part of stored data are deleted"""
        data = {'key1': 'value1'}
        test_file1 = 'test1.cpickle'
        test_file2 = 'test2.cpickle'

        def filter_func(file):
            if file == test_file1:
                return True
            else:
                return False

        self.wf.store_data('test1', data)
        self.wf.store_data('test2', data)

        self.assertTrue(os.path.exists(self.wf.datafile(test_file1)))
        self.assertTrue(os.path.exists(self.wf.datafile(test_file2)))
        self.wf.clear_data(filter_func)
        self.assertFalse(os.path.exists(self.wf.datafile(test_file1)))
        self.assertTrue(os.path.exists(self.wf.datafile(test_file2)))
        self.wf.clear_data()
        self.assertFalse(os.path.exists(self.wf.datafile(test_file2)))

    ####################################################################
    # Keychain
    ####################################################################

    def test_keychain(self):
        """Save/get/delete password"""
        self.assertRaises(PasswordNotFound,
                          self.wf.delete_password, self.account)
        self.assertRaises(PasswordNotFound, self.wf.get_password, self.account)
        self.wf.save_password(self.account, self.password)
        self.assertEqual(self.wf.get_password(self.account), self.password)
        self.assertEqual(self.wf.get_password(self.account, BUNDLE_ID),
                         self.password)
        # try to set same password
        self.wf.save_password(self.account, self.password)
        self.assertEqual(self.wf.get_password(self.account), self.password)
        # try to set different password
        self.wf.save_password(self.account, self.password2)
        self.assertEqual(self.wf.get_password(self.account), self.password2)
        # try to set non-ASCII password
        self.wf.save_password(self.account, self.password3)
        self.assertEqual(self.wf.get_password(self.account), self.password3)
        # bad call to _call_security
        self.assertRaises(KeychainError, self.wf._call_security,
                          'pants', BUNDLE_ID, self.account)

    ####################################################################
    # Running workflow
    ####################################################################

    def test_run_fails(self):
        """Run fails"""
        def cb(wf):
            self.assertEqual(wf, self.wf)
            raise ValueError('Have an error')
        self.wf.name  # cause info.plist to be parsed
        self.wf.help_url = 'http://www.deanishe.net/alfred-workflow/'
        ret = self.wf.run(cb)
        self.assertEqual(ret, 1)
        # named after bundleid
        self.wf = Workflow()
        self.wf.bundleid
        ret = self.wf.run(cb)
        self.assertEqual(ret, 1)

    def test_run_fails_with_xml_output(self):
        """Run fails with XML output"""
        error_text = 'Have an error'

        def cb(wf):
            self.assertEqual(wf, self.wf)
            raise ValueError(error_text)

        # named after bundleid
        self.wf = Workflow()
        self.wf.bundleid

        stdout = sys.stdout
        sio = StringIO()
        sys.stdout = sio
        ret = self.wf.run(cb)
        sys.stdout = stdout
        output = sio.getvalue()
        sio.close()

        self.assertEqual(ret, 1)
        self.assertTrue(error_text in output)
        self.assertTrue('<?xml' in output)

    def test_run_fails_with_plain_text_output(self):
        """Run fails with plain text output"""
        error_text = 'Have an error'

        def cb(wf):
            self.assertEqual(wf, self.wf)
            raise ValueError(error_text)

        # named after bundleid
        self.wf = Workflow()
        self.wf.bundleid

        stdout = sys.stdout
        sio = StringIO()
        sys.stdout = sio
        ret = self.wf.run(cb, text_errors=True)
        sys.stdout = stdout
        output = sio.getvalue()
        sio.close()

        self.assertEqual(ret, 1)
        self.assertTrue(error_text in output)
        self.assertTrue('<?xml' not in output)

    def test_run_fails_borked_settings(self):
        """Run fails with borked settings.json"""

        def fake(wf):
            wf.settings

        # Create invalid settings.json file
        with open(self.wf.settings_path, 'wb') as fp:
            fp.write('')

        ret = self.wf.run(fake)
        self.assertEqual(ret, 1)

    def test_run_okay(self):
        """Run okay"""
        def cb(wf):
            self.assertEqual(wf, self.wf)
        ret = self.wf.run(cb)
        self.assertEqual(ret, 0)

    ####################################################################
    # Filtering
    ####################################################################

    def test_filter_all_rules(self):
        """Filter: all rules"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True, match_on=MATCH_ALL)
        self.assertEqual(len(results), 8)
        # now with scores, rules
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 include_score=True, match_on=MATCH_ALL)
        self.assertEqual(len(results), 8)
        for item, score, rule in results:
            self.wf.logger.debug('%s : %s', item, score)
            for value, r in self.search_items:
                if value == item[0]:
                    self.assertEqual(rule, r)
        # self.assertTrue(False)

    def test_filter_no_caps(self):
        """Filter: no caps"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True,
                                 match_on=MATCH_ALL ^ MATCH_CAPITALS,
                                 include_score=True)
        self._print_results(results)
        for _, _, rule in results:
            self.assertNotEqual(rule, MATCH_CAPITALS)
        # self.assertEqual(len(results), 7)

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
        self.assertEqual(len(results), 4)

    def test_filter_min_score(self):
        """Filter: min score"""
        results = self.wf.filter('test', self.search_items, key=lambda x: x[0],
                                 ascending=True, min_score=90,
                                 include_score=True)
        self.assertEqual(len(results), 6)

    def test_filter_folding(self):
        """Filter: diacritic folding"""
        for key, query in self.search_items_diacritics:
            results = self.wf.filter(query, [key], min_score=90,
                                     include_score=True)
            self.assertEqual(len(results), 1)

    def test_filter_no_folding(self):
        """Filter: folding turned off for non-ASCII query"""
        data = ['fühler', 'fuhler', 'fübar', 'fubar']
        results = self.wf.filter('fü', data)
        self.assertEquals(len(results), 2)

    def test_filter_folding_off(self):
        """Filter: diacritic folding off"""
        for key, query in self.search_items_diacritics:
            results = self.wf.filter(query, [key], min_score=90,
                                     include_score=True,
                                     fold_diacritics=False)
            self.assertEqual(len(results), 0)

    def test_filter_folding_force_on(self):
        """Filter: diacritic folding forced on"""
        self.wf.settings['__workflow_diacritic_folding'] = True
        for key, query in self.search_items_diacritics:
            results = self.wf.filter(query, [key], min_score=90,
                                     include_score=True,
                                     fold_diacritics=False)
            self.assertEqual(len(results), 1)

    def test_filter_folding_force_off(self):
        """Filter: diacritic folding forced off"""
        self.wf.settings['__workflow_diacritic_folding'] = False
        for key, query in self.search_items_diacritics:
            results = self.wf.filter(query, [key], min_score=90,
                                     include_score=True)
            self.assertEqual(len(results), 0)

    def test_filter_empty_key(self):
        """Filter: empty keys are ignored"""
        data = ['bob', 'sue', 'henry']

        def key(s):
            """Return empty key"""
            return ''

        results = self.wf.filter('lager', data, key)
        self.assertEquals(len(results), 0)

    def test_filter_empty_query_words(self):
        """Filter: empty query returns all results"""
        data = ['bob', 'sue', 'henry']
        self.assertEquals(self.wf.filter('   ', data), data)
        self.assertEquals(self.wf.filter('', data), data)

    def test_filter_empty_query_words_ignored(self):
        """Filter: empty query words ignored"""
        data = ['bob jones', 'sue smith', 'henry rogers']
        results = self.wf.filter('bob       jones', data)
        self.assertEquals(len(results), 1)

    def test_filter_identical_items(self):
        """Filter: identical items are not discarded"""
        data = ['bob', 'bob', 'bob']
        results = self.wf.filter('bob', data)
        self.assertEquals(len(results), len(data))

    def test_filter_reversed_results(self):
        """Filter: results reversed"""
        data = ['bob', 'bobby', 'bobby smith']
        results = self.wf.filter('bob', data)
        self.assertEquals(results, data)
        results = self.wf.filter('bob', data, ascending=True)
        self.assertEquals(results, data[::-1])

    def test_punctuation(self):
        """Punctuation: dumbified"""
        for input, output in self.punctuation_data:
            self.assertEqual(self.wf.dumbify_punctuation(input), output)

    def test_icons(self):
        """Icons"""
        import workflow
        for name in dir(workflow):
            if name.startswith('ICON_'):
                path = getattr(workflow, name)
                print(name, path)
                self.assert_(os.path.exists(path))

    ####################################################################
    # Unicode properties
    ####################################################################

    def test_datadir_is_unicode(self):
        """Workflow.datadir returns Unicode"""
        wf = Workflow()
        self.assertTrue(isinstance(wf.datadir, unicode))
        self._teardown_env()
        wf = Workflow()
        self.assertTrue(isinstance(wf.datadir, unicode))

    def test_datafile_is_unicode(self):
        """Workflow.datafile returns Unicode"""
        wf = Workflow()
        self.assertTrue(isinstance(wf.datafile(b'test.txt'), unicode))
        self.assertTrue(isinstance(wf.datafile('über.txt'), unicode))
        self._teardown_env()
        wf = Workflow()
        self.assertTrue(isinstance(wf.datafile(b'test.txt'), unicode))
        self.assertTrue(isinstance(wf.datafile('über.txt'), unicode))

    def test_cachedir_is_unicode(self):
        """Workflow.cachedir returns Unicode"""
        wf = Workflow()
        self.assertTrue(isinstance(wf.cachedir, unicode))
        self._teardown_env()
        wf = Workflow()
        self.assertTrue(isinstance(wf.cachedir, unicode))

    def test_cachefile_is_unicode(self):
        """Workflow.cachefile returns Unicode"""
        wf = Workflow()
        self.assertTrue(isinstance(wf.cachefile(b'test.txt'), unicode))
        self.assertTrue(isinstance(wf.cachefile('über.txt'), unicode))
        self._teardown_env()
        wf = Workflow()
        self.assertTrue(isinstance(wf.cachefile(b'test.txt'), unicode))
        self.assertTrue(isinstance(wf.cachefile('über.txt'), unicode))

    def test_workflowdir_is_unicode(self):
        """Workflow.workflowdir returns Unicode"""
        wf = Workflow()
        self.assertTrue(isinstance(wf.workflowdir, unicode))

    def test_workflowfile_is_unicode(self):
        """Workflow.workflowfile returns Unicode"""
        wf = Workflow()
        self.assertTrue(isinstance(wf.workflowfile(b'test.txt'), unicode))
        self.assertTrue(isinstance(wf.workflowfile('über.txt'), unicode))

    ####################################################################
    # Versions
    ####################################################################

    def test_versions_from_settings(self):
        """Workflow: version from `update_settings`"""
        vstr = '1.9.7'
        d = {'github_slug': 'deanishe/alfred-workflow', 'version': vstr}
        wf = Workflow(update_settings=d)
        self.assertEqual(str(wf.version), vstr)
        self.assertTrue(isinstance(wf.version, Version))
        self.assertEqual(wf.version, Version(vstr))

    def test_versions_from_version_file(self):
        """Workflow: version from `version`"""
        vstr = '1.9.7'
        with VersionFile(vstr):
            with InfoPlist():
                wf = Workflow()
                self.assertEqual(str(wf.version), vstr)
                self.assertTrue(isinstance(wf.version, Version))
                self.assertEqual(wf.version, Version(vstr))

    def test_first_run_no_version(self):
        """Workflow: first_run fails on no version"""
        with InfoPlist():
            wf = Workflow()
            self.assertRaises(ValueError, lambda wf: wf.first_run, wf)

    def test_first_run_with_version(self):
        """Workflow: first_run"""
        vstr = '1.9.7'
        with VersionFile(vstr):
            with InfoPlist():
                wf = Workflow()
                self.assertTrue(wf.first_run)
            wf.reset()

    def test_first_run_with_previous_run(self):
        """Workflow: first_run with previous run"""
        vstr = '1.9.7'
        last_vstr = '1.9.6'
        with VersionFile(vstr):
            with InfoPlist():
                wf = Workflow()
                wf.set_last_version(last_vstr)
                self.assertTrue(wf.first_run)
                self.assertEqual(wf.last_version_run, Version(last_vstr))
            wf.reset()

    def test_last_version_empty(self):
        """Workflow: last_version_run empty"""
        wf = Workflow()
        self.assertTrue(wf.last_version_run is None)

    def test_last_version_on(self):
        """Workflow: last_version_run not empty"""
        vstr = '1.9.7'

        with InfoPlist():
            with VersionFile(vstr):
                wf = Workflow()
                wf.set_last_version(vstr)
                self.assertEqual(Version(vstr), wf.last_version_run)
                wf.reset()
            # Set automatically
            with VersionFile(vstr):
                wf = Workflow()
                wf.set_last_version()
                self.assertEqual(Version(vstr), wf.last_version_run)
                wf.reset()

    def test_versions_no_version(self):
        """Workflow: version is `None`"""
        wf = Workflow()
        self.assertTrue(wf.version is None)
        wf.reset()

    def test_last_version_no_version(self):
        """Workflow: last_version no version"""
        wf = Workflow()
        self.assertFalse(wf.set_last_version())
        wf.reset()

    def test_last_version_explicit_version(self):
        """Workflow: last_version explicit version"""
        vstr = '1.9.6'
        wf = Workflow()
        self.assertTrue(wf.set_last_version(vstr))
        self.assertEqual(wf.last_version_run, Version(vstr))
        wf.reset()

    def test_last_version_auto_version(self):
        """Workflow: last_version auto version"""
        vstr = '1.9.7'
        with VersionFile(vstr):
            with InfoPlist():
                wf = Workflow()
                self.assertTrue(wf.set_last_version())
                self.assertEqual(wf.last_version_run, Version(vstr))
                wf.reset()

    def test_last_version_set_after_run(self):
        """Workflow: last_version set after `run()`"""
        vstr = '1.9.7'

        def cb(wf):
            return

        with VersionFile(vstr):
            with InfoPlist():
                wf = Workflow()
                self.assertTrue(wf.last_version_run is None)
                wf.run(cb)

                wf = Workflow()
                self.assertEqual(wf.last_version_run, Version(vstr))
                wf.reset()

    def test_alfred_version(self):
        """Workflow: alfred_version correct."""
        wf = Workflow()
        self.assertEqual(wf.alfred_version, Version('2.4'))

    ####################################################################
    # Helpers
    ####################################################################

    def _print_results(self, results):
        """Print results of Workflow.filter"""
        for item, score, rule in results:
            print('{0!r} (rule {1}) : {2}'.format(item[0], rule, score))

    def _stored_data_paths(self, name, serializer):
        """Return list of paths created when storing data"""
        metadata = self.wf.datafile('.{0}.alfred-workflow'.format(name))
        datapath = self.wf.datafile('{0}.{1}'.format(name, serializer))
        return [metadata, datapath]

    def _setup_env(self, data=None):
        """Add Alfred env variables to environment."""
        self._original_env = os.environ.copy()
        data = data or self.env_data
        for key in data:
            os.environ[key] = data[key]

    def _teardown_env(self):
        """Remove Alfred env variables from environment."""
        os.environ = self._original_env


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
