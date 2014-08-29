#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-01
#
"""
test_workflow.py

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

from util import create_info_plist, delete_info_plist

from workflow.workflow import (Workflow, Settings, PasswordNotFound,
                               KeychainError, MATCH_ALL, MATCH_ALLCHARS,
                               MATCH_ATOM, MATCH_CAPITALS, MATCH_STARTSWITH,
                               MATCH_SUBSTRING, MATCH_INITIALS_CONTAIN,
                               MATCH_INITIALS_STARTSWITH,
                               manager)

# info.plist settings
BUNDLE_ID = 'net.deanishe.alfred-workflow'
WORKFLOW_NAME = 'Alfred-Workflow Test'

DEFAULT_SETTINGS = {'key1': 'value1',
                    'key2': 'hübner'}


def setUp():
    pass


def tearDown():
    pass


class SerializerTests(unittest.TestCase):

    def setUp(self):
        self.serializers = ['json', 'cpickle', 'pickle']
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def _is_serializer(self, obj):
        self.assertTrue(hasattr(obj, 'load'))
        self.assertTrue(hasattr(obj, 'dump'))

    def test_default_serializers(self):
        """Default serializers"""
        for name in self.serializers:
            self._is_serializer(manager.serializer(name))

        self.assertEqual(set(self.serializers), set(manager.serializers))

    def test_serialization(self):
        """Dump/load data"""
        data = {'arg1': 'value1', 'arg2': 'value2'}

        for name in self.serializers:
            serializer = manager.serializer(name)
            path = os.path.join(self.tempdir, 'test.{}'.format(name))
            self.assertFalse(os.path.exists(path))

            with open(path, 'wb') as file_obj:
                serializer.dump(data, file_obj)

            self.assertTrue(os.path.exists(path))

            with open(path, 'rb') as file_obj:
                data2 = serializer.load(file_obj)

            self.assertEqual(data, data2)

            os.unlink(path)

    def test_register_unregister(self):
        """Register/unregister serializers"""
        serializers = {}
        for name in self.serializers:
            serializer = manager.serializer(name)
            self._is_serializer(serializer)

        for name in self.serializers:
            serializer = manager.unregister(name)
            self._is_serializer(serializer)
            serializers[name] = serializer

        for name in self.serializers:
            self.assertEqual(manager.serializer(name), None)

        for name in self.serializers:
            with self.assertRaises(ValueError):
                manager.unregister(name)

        for name in self.serializers:
            serializer = serializers[name]
            manager.register(name, serializer)

    def test_register_invalid(self):
        """Register invalid serializer"""
        class Thing(object):
            pass
        invalid1 = Thing()
        invalid2 = Thing()
        setattr(invalid2, 'load', lambda x: x)

        with self.assertRaises(AttributeError):
            manager.register('bork', invalid1)
        with self.assertRaises(AttributeError):
            manager.register('bork', invalid2)


class WorkflowTests(unittest.TestCase):

    def setUp(self):
        self.libs = [os.path.join(os.path.dirname(__file__), b'lib')]
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

        self.env_data = {
            'alfred_preferences':
            os.path.expanduser('~/Dropbox/Alfred/Alfred.alfredpreferences'),
            'alfred_preferences_localhash':
            b'adbd4f66bc3ae8493832af61a41ee609b20d8705',
            'alfred_theme': b'alfred.theme.yosemite',
            'alfred_theme_background': b'rgba(255,255,255,0.98)',
            'alfred_theme_subtext': b'3',
            'alfred_version': b'2.4',
            'alfred_version_build': b'277',
            'alfred_workflow_bundleid': str(BUNDLE_ID),
            'alfred_workflow_cache':
            os.path.expanduser('~/Library/Caches/com.runningwithcrayons.'
                               'Alfred-2/Workflow Data/{}'.format(BUNDLE_ID)),
            'alfred_workflow_data':
            os.path.expanduser('~/Library/Application Support/Alfred 2/'
                               'Workflow Data/{}'.format(BUNDLE_ID)),
            'alfred_workflow_name': b'Alfred-Workflow Test',
            'alfred_workflow_uid':
            b'user.workflow.B0AC54EC-601C-479A-9428-01F9FD732959',
        }

        self._setup_env()

        self.wf = Workflow(libraries=self.libs)

    def tearDown(self):
        self.wf.reset()
        try:
            self.wf.delete_password(self.account)
        except PasswordNotFound:
            pass

        for dirpath in (self.wf.cachedir, self.wf.datadir):
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)

        self._teardown_env()

    def test_item_creation(self):
        """XML generation"""
        self.wf.add_item('title', 'subtitle', arg='arg',
                         autocomplete='autocomplete',
                         valid=True, uid='uid', icon='icon.png',
                         icontype='fileicon',
                         type='file', largetext='largetext',
                         copytext='copytext')
        stdout = sys.stdout
        sio = StringIO()
        sys.stdout = sio
        self.wf.send_feedback()
        sys.stdout = stdout
        output = sio.getvalue()
        sio.close()
        from pprint import pprint
        pprint(output)

        root = ET.fromstring(output)
        item = list(root)[0]

        self.assertEqual(item.attrib['uid'], 'uid')
        self.assertEqual(item.attrib['autocomplete'], 'autocomplete')
        self.assertEqual(item.attrib['valid'], 'yes')
        self.assertEqual(item.attrib['uid'], 'uid')

        title, subtitle, arg, icon, largetext, copytext = list(item)

        self.assertEqual(title.text, 'title')
        self.assertEqual(title.tag, 'title')

        self.assertEqual(subtitle.text, 'subtitle')
        self.assertEqual(subtitle.tag, 'subtitle')

        self.assertEqual(arg.text, 'arg')
        self.assertEqual(arg.tag, 'arg')

        self.assertEqual(largetext.tag, 'text')
        self.assertEqual(largetext.text, 'largetext')
        self.assertEqual(largetext.attrib['type'], 'largetype')

        self.assertEqual(copytext.tag, 'text')
        self.assertEqual(copytext.text, 'copytext')
        self.assertEqual(copytext.attrib['type'], 'copy')

        self.assertEqual(icon.text, 'icon.png')
        self.assertEqual(icon.tag, 'icon')
        self.assertEqual(icon.attrib['type'], 'fileicon')

    def test_item_creation_with_modifiers(self):
        """XML generation (with modifiers)"""
        mod_subs = {}
        for mod in ('cmd', 'ctrl', 'alt', 'shift', 'fn'):
            mod_subs[mod] = mod
        self.wf.add_item('title', 'subtitle',
                         mod_subs,
                         arg='arg',
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
        from pprint import pprint
        pprint(output)
        root = ET.fromstring(output)
        item = list(root)[0]
        self.assertEqual(item.attrib['uid'], 'uid')
        self.assertEqual(item.attrib['autocomplete'], 'autocomplete')
        self.assertEqual(item.attrib['valid'], 'yes')
        self.assertEqual(item.attrib['uid'], 'uid')
        (title, subtitle, sub_cmd, sub_ctrl, sub_alt, sub_shift, sub_fn, arg,
         icon) = list(item)
        self.assertEqual(title.text, 'title')
        self.assertEqual(title.tag, 'title')
        self.assertEqual(subtitle.text, 'subtitle')
        self.assertEqual(sub_cmd.text, 'cmd')
        self.assertEqual(sub_cmd.attrib['mod'], 'cmd')
        self.assertEqual(sub_ctrl.text, 'ctrl')
        self.assertEqual(sub_ctrl.attrib['mod'], 'ctrl')
        self.assertEqual(sub_alt.text, 'alt')
        self.assertEqual(sub_alt.attrib['mod'], 'alt')
        self.assertEqual(sub_shift.text, 'shift')
        self.assertEqual(sub_shift.attrib['mod'], 'shift')
        self.assertEqual(sub_fn.text, 'fn')
        self.assertEqual(sub_fn.attrib['mod'], 'fn')
        self.assertEqual(subtitle.tag, 'subtitle')
        self.assertEqual(arg.text, 'arg')
        self.assertEqual(arg.tag, 'arg')
        self.assertEqual(icon.text, 'icon.png')
        self.assertEqual(icon.tag, 'icon')
        self.assertEqual(icon.attrib['type'], 'fileicon')

    def test_item_creation_no_optionals(self):
        """XML generation (no optionals)"""
        self.wf.add_item('title')
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
        self.assertEqual(item.attrib['valid'], 'no')
        title, subtitle = list(item)
        self.assertEqual(title.text, 'title')
        self.assertEqual(title.tag, 'title')
        self.assertEqual(subtitle.text, None)
        tags = [elem.tag for elem in list(item)]
        for tag in ['icon', 'arg']:
            self.assert_(tag not in tags)

    def test_additional_libs(self):
        """Additional libraries"""
        for path in self.libs:
            self.assert_(path in sys.path)
        self.assertEqual(sys.path[0:len(self.libs)], self.libs)
        import youcanimportme

    def test_info_plist(self):
        """info.plist"""
        self._teardown_env()
        self.assertEqual(self.wf.name, WORKFLOW_NAME)
        self.assertEqual(self.wf.bundleid, BUNDLE_ID)

    def test_info_plist_missing(self):
        """Info.plist missing"""
        delete_info_plist()
        self._teardown_env()
        try:
            with self.assertRaises(IOError):
                Workflow()
        finally:
            create_info_plist()

    def test_alfred_env_vars(self):
        """Alfred environmental variables"""

        self._setup_env()

        for key in self.env_data:
            value = self.env_data[key]
            key = key.replace('alfred_', '')
            self.assertEqual(value, self.wf.alfred_env[key])

        self.assertEqual(self.wf.datadir, self.env_data['alfred_workflow_data'])
        self.assertEqual(self.wf.cachedir,
                         self.env_data['alfred_workflow_cache'])
        self.assertEqual(self.wf.bundleid,
                         self.env_data['alfred_workflow_bundleid'])
        self.assertEqual(self.wf.name,
                         self.env_data['alfred_workflow_name'])

        self._teardown_env()

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
            return normalize('NFD', s)
        args = map(nfdme, ['arg1', 'arg2', 'füntíme'])
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
            self.assertTrue(os.path.exists(wf.cachefile('test.cpickle')))
            with self.assertRaises(SystemExit):
                wf.args
            self.assertFalse(os.path.exists(wf.cachefile('test.cpickle')))
        finally:
            sys.argv = oargs[:]

    def test_logger(self):
        """Logger"""
        self.assert_(isinstance(self.wf.logger, logging.Logger))
        logger = logging.Logger('')
        self.wf.logger = logger
        self.assertEqual(self.wf.logger, logger)

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

    def test_cache_serializer(self):
        """Cache serializer"""
        self.assertEqual(self.wf.cache_serializer, 'cpickle')
        with self.assertRaises(ValueError):
            self.wf.cache_serializer = 'non-existent'
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
            @classmethod
            def load(self, file_obj):
                return json.load(file_obj)

            @classmethod
            def dump(self, obj, file_obj):
                return json.dump(obj, file_obj, indent=2)

        manager.register('spoons', MySerializer)
        self.assertFalse(os.path.exists(self.wf.cachefile('test.spoons')))
        self.wf.cache_serializer = 'spoons'
        self.wf.cache_data('test', data)
        self.assertTrue(os.path.exists(self.wf.cachefile('test.spoons')))
        self.assertEqual(data, self.wf.cached_data('test'))

    def test_data_serializer(self):
        """Data serializer"""
        self.assertEqual(self.wf.data_serializer, 'cpickle')
        with self.assertRaises(ValueError):
            self.wf.data_serializer = 'non-existent'
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
        self.assertIsNone(self.wf.stored_data('banjo magic'))

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
        self.assertIsNone(self.wf.stored_data('test'))

        self.wf.store_data('test', data)
        metadata, datapath = self._stored_data_paths('test', 'cpickle')
        with open(metadata, 'wb') as file_obj:
            file_obj.write('bangers and mash')
            self.wf.logger.debug('Changed format to `bangers and mash`')
        with self.assertRaises(ValueError):
            self.wf.stored_data('test')

    def test_reject_settings(self):
        """Disallow settings.json"""
        data = {'key7': 'value7'}

        self.wf.data_serializer = 'json'

        with self.assertRaises(ValueError):
            self.wf.store_data('settings', data)

    def test_invalid_data_serializer(self):
        """Invalid data serializer"""
        data = {'key7': 'value7'}

        with self.assertRaises(ValueError):
            self.wf.store_data('test', data, 'spong')

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

    def test_update(self):
        """Workflow updating methods"""
        self.assertFalse(self.wf.update_available)
        self.wf = Workflow(update_info={
            'github_slug': 'fniephaus/alfred-pocket',
            'version': 'v0.0',
            'frequency': 1,
        })
        # wait for background update check
        time.sleep(2)
        self.assertTrue(self.wf.update_available)
        self.assertTrue(self.wf.start_update())
        update_info = self.wf.cached_data('__workflow_update_available')
        self.wf = Workflow(update_info={
            'github_slug': 'fniephaus/alfred-pocket',
            'version': update_info['version'],
        })
        # wait for background update check
        time.sleep(2)
        self.assertFalse(self.wf.update_available)
        self.assertFalse(self.wf.start_update())

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
        # bad call to _call_security
        with self.assertRaises(KeychainError):
            self.wf._call_security('pants', BUNDLE_ID, self.account)

    def test_run_fails(self):
        """Run fails"""
        def cb(wf):
            self.assertEqual(wf, self.wf)
            raise ValueError('Have an error')
        self.wf.name  # cause info.plist to be parsed
        ret = self.wf.run(cb)
        self.assertEqual(ret, 1)
        # named after bundleid
        self.wf = Workflow()
        self.wf.bundleid
        ret = self.wf.run(cb)
        self.assertEqual(ret, 1)

    def test_run_okay(self):
        """Run okay"""
        def cb(wf):
            self.assertEqual(wf, self.wf)
        ret = self.wf.run(cb)
        self.assertEqual(ret, 0)

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
            self.wf.logger.debug('{} : {}'.format(item, score))
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
        for item, score, rule in results:
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
            return ''

        results = self.wf.filter('lager', data, key)
        self.assertEquals(len(results), 0)

    def test_filter_empty_query_words(self):
        """Filter: empty query words are ignored"""
        data = ['bob', 'sue', 'henry']
        results = self.wf.filter('   ', data)
        self.assertEquals(len(results), 0)

    def test_filter_identical_items(self):
        """Filter: identical items are not discarded"""
        data = ['bob', 'bob', 'bob']
        results = self.wf.filter('bob', data)
        self.assertEquals(len(results), len(data))

    def test_icons(self):
        """Icons"""
        import workflow
        for name in dir(workflow):
            if name.startswith('ICON_'):
                path = getattr(workflow, name)
                print(name, path)
                self.assert_(os.path.exists(path))

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

    def _print_results(self, results):
        """Print results of Workflow.filter"""
        for item, score, rule in results:
            print('{!r} (rule {}) : {}'.format(item[0], rule, score))

    def _stored_data_paths(self, name, serializer):
        """Return list of paths created when storing data"""
        metadata = self.wf.datafile('.{}.alfred-workflow'.format(name))
        datapath = self.wf.datafile('{}.{}'.format(name, serializer))
        return [metadata, datapath]

    def _setup_env(self):
        """Add Alfred env variables to environment"""

        for key in self.env_data:
            os.environ[key] = self.env_data[key]

    def _teardown_env(self):
        """Remove Alfred env variables from environment"""

        for key in self.env_data:
            if key in os.environ:
                del os.environ[key]


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


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
