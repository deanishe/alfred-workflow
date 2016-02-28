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

import json
import logging
import os
import shutil
import signal
from StringIO import StringIO
import sys
import tempfile
import time
import unittest

from xml.etree import ElementTree as ET
from unicodedata import normalize

from util import (
    # create_info_plist, delete_info_plist,
    WorkflowMock,
    VersionFile,
    InfoPlist,
    INFO_PLIST_TEST,
    INFO_PLIST_PATH,
    create_info_plist,
    delete_info_plist,
    DEFAULT_SETTINGS,
)

from workflow.workflow import (Workflow, PasswordNotFound,
                               KeychainError, MATCH_ALL, MATCH_ALLCHARS,
                               MATCH_ATOM, MATCH_CAPITALS, MATCH_STARTSWITH,
                               MATCH_SUBSTRING, MATCH_INITIALS_CONTAIN,
                               MATCH_INITIALS_STARTSWITH,
                               manager, atomic_writer, uninterruptible)

from workflow.update import Version

# info.plist settings
BUNDLE_ID = 'net.deanishe.alfred-workflow'
WORKFLOW_NAME = 'Alfred-Workflow Test'


def setUp():
    pass


def tearDown():
    pass


class SerializerTests(unittest.TestCase):
    """Test workflow.manager serialisation API"""

    def setUp(self):
        self.serializers = ['json', 'cpickle', 'pickle']
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def _is_serializer(self, obj):
        """Does `obj` implement the serializer API?"""
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
            path = os.path.join(self.tempdir, 'test.{0}'.format(name))
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
            self.assertRaises(ValueError, manager.unregister, name)

        for name in self.serializers:
            serializer = serializers[name]
            manager.register(name, serializer)

    def test_register_invalid(self):
        """Register invalid serializer"""
        class Thing(object):
            """Bad serializer"""
            pass
        invalid1 = Thing()
        invalid2 = Thing()
        setattr(invalid2, 'load', lambda x: x)

        self.assertRaises(AttributeError, manager.register, 'bork', invalid1)
        self.assertRaises(AttributeError, manager.register, 'bork', invalid2)


class WorkflowTests(unittest.TestCase):
    """Test suite for workflow.workflow.Workflow"""

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
    # Result item generation
    ####################################################################

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
            # wf = Workflow()
            self.assertFalse(os.path.exists(INFO_PLIST_PATH))
            # self.assertRaises(IOError, lambda wf: wf.info, wf)
            self.assertRaises(IOError, Workflow)
        # try:
        #     self.assertRaises(IOError, Workflow)
        # finally:
        #     create_info_plist()

    def test_alfred_env_vars(self):
        """Alfred environmental variables"""

        self._setup_env()

        for key in self.env_data:
            value = self.env_data[key]
            key = key.replace('alfred_', '')
            if key in ('version_build', 'theme_subtext'):
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

        self._teardown_env()

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
        self.assertFalse(os.path.exists(self.wf.cachefile('test.spoons')))
        self.wf.cache_serializer = 'spoons'
        self.wf.cache_data('test', data)
        self.assertTrue(os.path.exists(self.wf.cachefile('test.spoons')))
        self.assertEqual(data, self.wf.cached_data('test'))

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
            self.wf.logger.debug('{0} : {1}'.format(item, score))
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
            """Return empty key"""
            return ''

        results = self.wf.filter('lager', data, key)
        self.assertEquals(len(results), 0)

    def test_filter_empty_query_words(self):
        """Filter: empty query raises error"""
        data = ['bob', 'sue', 'henry']
        self.assertRaises(ValueError, self.wf.filter, '   ', data)

        self.assertRaises(ValueError, self.wf.filter, '', data)

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

    def _setup_env(self):
        """Add Alfred env variables to environment"""

        for key in self.env_data:
            os.environ[key] = self.env_data[key]

    def _teardown_env(self):
        """Remove Alfred env variables from environment"""

        for key in self.env_data:
            if key in os.environ:
                del os.environ[key]


class MagicArgsTests(unittest.TestCase):
    """Test magic arguments"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_list_magic(self):
        """Magic: list magic"""
        # TODO: Verify output somehow
        c = WorkflowMock(['script', 'workflow:magic'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(len(c.cmd), 0)
            wf.logger.debug('STDERR : {0}'.format(c.stderr))

    def test_version_magic(self):
        """Magic: version magic"""
        # TODO: Verify output somehow

        vstr = '1.9.7'

        # Versioned
        c = WorkflowMock(['script', 'workflow:version'])
        with InfoPlist():
            with c:
                with VersionFile(vstr):
                    wf = Workflow()
                    # Process magic arguments
                    wf.args
            self.assertEquals(len(c.cmd), 0)
            wf.logger.debug('STDERR : {0}'.format(c.stderr))

            # Unversioned
            c = WorkflowMock(['script', 'workflow:version'])
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(len(c.cmd), 0)

    def test_openhelp(self):
        """Magic: open help URL"""
        url = 'http://www.deanishe.net/alfred-workflow/'
        c = WorkflowMock(['script', 'workflow:help'])
        with InfoPlist():
            with c:
                wf = Workflow(help_url=url)
                # Process magic arguments
                wf.args
            self.assertEquals(c.cmd[0], 'open')
            self.assertEquals(c.cmd[1], url)

    def test_openhelp_no_url(self):
        """Magic: no help URL"""
        c = WorkflowMock(['script', 'workflow:help'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(len(c.cmd), 0)

    def test_openlog(self):
        """Magic: open logfile"""
        c = WorkflowMock(['script', 'workflow:openlog'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(c.cmd[0], 'open')
            self.assertEquals(c.cmd[1], wf.logfile)

    def test_cachedir(self):
        """Magic: open cachedir"""
        c = WorkflowMock(['script', 'workflow:opencache'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(c.cmd[0], 'open')
            self.assertEquals(c.cmd[1], wf.cachedir)

    def test_datadir(self):
        """Magic: open datadir"""
        c = WorkflowMock(['script', 'workflow:opendata'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(c.cmd[0], 'open')
            self.assertEquals(c.cmd[1], wf.datadir)

    def test_workflowdir(self):
        """Magic: open workflowdir"""
        c = WorkflowMock(['script', 'workflow:openworkflow'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(c.cmd[0], 'open')
            self.assertEquals(c.cmd[1], wf.workflowdir)

    def test_open_term(self):
        """Magic: open Terminal"""
        c = WorkflowMock(['script', 'workflow:openterm'])
        with InfoPlist():
            with c:
                wf = Workflow()
                # Process magic arguments
                wf.args
            self.assertEquals(c.cmd, ['open', '-a', 'Terminal', wf.workflowdir])

    def test_delete_data(self):
        """Magic: delete data"""
        c = WorkflowMock(['script', 'workflow:deldata'])
        with InfoPlist():
            wf = Workflow()
            testpath = wf.datafile('file.test')
            with open(testpath, 'wb') as file_obj:
                file_obj.write('test!')
            with c:
                self.assertTrue(os.path.exists(testpath))
                # Process magic arguments
                wf.args
                self.assertFalse(os.path.exists(testpath))

    def test_delete_cache(self):
        """Magic: delete cache"""
        c = WorkflowMock(['script', 'workflow:delcache'])
        with InfoPlist():
            wf = Workflow()
            testpath = wf.cachefile('file.test')
            with open(testpath, 'wb') as file_obj:
                file_obj.write('test!')
            with c:
                self.assertTrue(os.path.exists(testpath))
                # Process magic arguments
                wf.args
                self.assertFalse(os.path.exists(testpath))

    def test_reset(self):
        """Magic: reset"""
        with InfoPlist():
            wf = Workflow()
            wf.settings['key'] = 'value'
            datatest = wf.datafile('data.test')
            cachetest = wf.cachefile('cache.test')
            settings_path = wf.datafile('settings.json')

            for p in (datatest, cachetest):
                with open(p, 'wb') as file_obj:
                    file_obj.write('test!')

            for p in (datatest, cachetest, settings_path):
                self.assertTrue(os.path.exists(p))

            c = WorkflowMock(['script', 'workflow:reset'])
            with c:
                wf.args

            for p in (datatest, cachetest, settings_path):
                self.assertFalse(os.path.exists(p))

    def test_delete_settings(self):
        """Magic: delete settings"""
        c = WorkflowMock(['script', 'workflow:delsettings'])
        with InfoPlist():
            wf = Workflow()
            wf.settings['key'] = 'value'
            filepath = wf.datafile('settings.json')
            with c:
                self.assertTrue(os.path.exists(filepath))
                wf2 = Workflow()
                self.assertEquals(wf2.settings.get('key'), 'value')
                # Process magic arguments
                wf.args
                self.assertFalse(os.path.exists(filepath))
                wf3 = Workflow()
                self.assertFalse('key' in wf3.settings)

    def test_folding(self):
        """Magic: folding"""
        with InfoPlist():
            wf = Workflow()
            c = WorkflowMock(['script', 'workflow:foldingdefault'])
            with c:
                wf.args
            self.assertTrue(wf.settings.get('__workflow_diacritic_folding')
                            is None)

            wf = Workflow()
            c = WorkflowMock(['script', 'workflow:foldingon'])
            with c:
                wf.args
            self.assertTrue(wf.settings.get('__workflow_diacritic_folding'))

            wf = Workflow()
            c = WorkflowMock(['script', 'workflow:foldingdefault'])
            with c:
                wf.args
            self.assertTrue(wf.settings.get('__workflow_diacritic_folding') is
                            None)

            wf = Workflow()
            c = WorkflowMock(['script', 'workflow:foldingoff'])
            with c:
                wf.args
            self.assertFalse(wf.settings.get('__workflow_diacritic_folding'))

    def test_auto_update(self):
        """Magic: auto-update"""

        update_settings = {
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'frequency': 1,
        }

        def fake(wf):
            return

        with InfoPlist():
            wf = Workflow(update_settings=update_settings)
            c = WorkflowMock(['script', 'workflow:autoupdate'])
            with c:
                wf.args
                wf.run(fake)
            self.assertTrue(wf.settings.get('__workflow_autoupdate'))

            wf = Workflow(update_settings=update_settings)
            wf.reset()
            c = WorkflowMock(['script', 'workflow:noautoupdate'])
            with c:
                wf.args
                wf.run(fake)
            self.assertFalse(wf.settings.get('__workflow_autoupdate'))

            # del wf.settings['__workflow_autoupdate']
            wf.reset()

    def test_prereleases(self):
        """Magic: pre-release updates"""

        update_settings = {
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'frequency': 1,
        }

        def fake(wf):
            return

        with InfoPlist():
            wf = Workflow(update_settings=update_settings)
            c = WorkflowMock(['script', 'workflow:prereleases'])
            with c:
                wf.args
                wf.run(fake)
            self.assertTrue(wf.settings.get('__workflow_prereleases'))

            wf = Workflow(update_settings=update_settings)
            wf.reset()
            c = WorkflowMock(['script', 'workflow:noprereleases'])
            with c:
                wf.args
                wf.run(fake)
            self.assertFalse(wf.settings.get('__workflow_prereleases'))

            wf.reset()

    def test_update_settings_override_magic_prereleases(self):
        """Magic: pre-release updates can be overridden by `True` value for `prereleases` key in `update_settings`"""

        update_settings = {
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'frequency': 1,
            'prereleases': False,
        }

        def fake(wf):
            return

        # Normal behavior
        with InfoPlist():
            wf = Workflow(update_settings=update_settings)
            c = WorkflowMock(['script', 'workflow:prereleases'])
            with c:
                wf.args
                wf.run(fake)
            self.assertTrue(wf.prereleases)

            wf = Workflow(update_settings=update_settings)
            wf.reset()
            c = WorkflowMock(['script', 'workflow:noprereleases'])
            with c:
                wf.args
                wf.run(fake)
            self.assertFalse(wf.prereleases)

            wf.reset()

        update_settings['prereleases'] = True

        # Pre-release enabled regardless of preference
        with InfoPlist():
            wf = Workflow(update_settings=update_settings)
            c = WorkflowMock(['script', 'workflow:prereleases'])
            with c:
                wf.args
                wf.run(fake)
            self.assertTrue(wf.prereleases)

            wf = Workflow(update_settings=update_settings)
            wf.reset()
            c = WorkflowMock(['script', 'workflow:noprereleases'])
            with c:
                wf.args
                wf.run(fake)
            self.assertTrue(wf.prereleases)

            wf.reset()

    def test_update(self):
        """Magic: update"""

        def fake(wf):
            return

        update_settings = {
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'frequency': 1,
        }
        with InfoPlist():
            wf = Workflow(update_settings=update_settings)
            wf.run(fake)

            self.assertFalse(wf.update_available)

            # Mock subprocess.call etc. so the script doesn't try to
            # update the workflow in Alfred
            c = WorkflowMock(['script', 'workflow:update'])
            with c:
                wf.run(fake)
                wf.args

            wf.logger.debug('Magic update command : {0}'.format(c.cmd))

            self.assertEquals(c.cmd[0], '/usr/bin/python')
            self.assertEquals(c.cmd[2], '__workflow_update_install')

            update_settings['version'] = 'v6.0'
            wf = Workflow(update_settings=update_settings)
            c = WorkflowMock(['script', 'workflow:update'])
            with c:
                wf.run(fake)
                wf.args

            # Update command wasn't called
            self.assertEqual(c.cmd, ())

    def test_update_turned_off(self):
        """Magic: updates turned off"""

        # Check update isn't performed if user has turned off
        # auto-update

        def fake(wf):
            return

        update_settings = {
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'frequency': 1,
        }
        with InfoPlist():
            wf = Workflow(update_settings=update_settings)
            wf.settings['__workflow_autoupdate'] = False
            self.assertTrue(wf.check_update() is None)


class AtomicWriterTests(unittest.TestCase):
    """Tests for atomic writer"""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.tempdir, 'settings.json')

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_write_file_succeed(self):
        """AtomicWriter: Succeed, no temp file left"""
        with atomic_writer(self.settings_file, 'wb') as file_obj:
            json.dump(DEFAULT_SETTINGS, file_obj)
        self.assertEqual(len(os.listdir(self.tempdir)), 1)
        self.assertTrue(os.path.exists(self.settings_file))

    def test_failed_before_writing(self):
        """AtomicWriter: Exception before writing"""
        def write_function():
            with atomic_writer(self.settings_file, 'wb'):
                raise Exception()

        self.assertRaises(Exception, write_function)
        self.assertEqual(len(os.listdir(self.tempdir)), 0)

    def test_failed_after_writing(self):
        """AtomicWriter: Exception after writing"""
        def write_function():
            with atomic_writer(self.settings_file, 'wb') as file_obj:
                json.dump(DEFAULT_SETTINGS, file_obj)
                raise Exception()

        self.assertRaises(Exception, write_function)
        self.assertEqual(len(os.listdir(self.tempdir)), 0)

    def test_failed_without_overwriting(self):
        """AtomicWriter: Exception after writing won't overwrite the old file"""
        mockSettings = {}

        def write_function():
            with atomic_writer(self.settings_file, 'wb') as file_obj:
                json.dump(mockSettings, file_obj)
                raise Exception()

        with atomic_writer(self.settings_file, 'wb') as file_obj:
            json.dump(DEFAULT_SETTINGS, file_obj)
        self.assertEqual(len(os.listdir(self.tempdir)), 1)
        self.assertTrue(os.path.exists(self.settings_file))

        self.assertRaises(Exception, write_function)
        self.assertEqual(len(os.listdir(self.tempdir)), 1)
        self.assertTrue(os.path.exists(self.settings_file))

        with open(self.settings_file, 'rb') as file_obj:
            real_settings = json.load(file_obj)
            self.assertEqual(DEFAULT_SETTINGS, real_settings)


class UninterruptibleTests(unittest.TestCase):
    """Test for multiple files atomic writer"""

    @uninterruptible
    def _mock_write_function(self):
        if self.kill_flag:
            self.kill_flag = False
            self._kill()
        self.result_flag = True

    def _old_signal_handler(self, s, f):
            self.old_signal_flag = True

    def _kill(self):
        os.kill(os.getpid(), signal.SIGTERM)

    def setUp(self):
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

        self.result_flag = False  # True if the write_function is executed
        self.old_signal_flag = False  # True if old signal handler is executed
        self.kill_flag = True  # True if process should be killed

    def test_normal(self):
        """Uninterruptible: Normal writing operator"""
        self.kill_flag = False

        self._mock_write_function()

        self.assertTrue(self.result_flag)

    def test_sigterm_signal(self):
        """Uninterruptible: Process is killed"""
        self.assertRaises(SystemExit, self._mock_write_function)

        self.assertTrue(self.result_flag)
        self.assertFalse(self.kill_flag)

    def test_old_signal_handler(self):
        """Uninterruptible: Process killed with some other signal handler"""
        signal.signal(signal.SIGTERM, self._old_signal_handler)

        self._mock_write_function()

        self.assertTrue(self.result_flag)
        self.assertTrue(self.old_signal_flag)
        self.assertFalse(self.kill_flag)

    def test_old_signal_handler_restore(self):
        """Uninterruptible: Previous signal handler is restored after write"""
        signal.signal(signal.SIGTERM, self._old_signal_handler)
        self.kill_flag = False

        self._mock_write_function()

        self.assertTrue(self.result_flag)
        self.assertEqual(signal.getsignal(signal.SIGTERM),
                         self._old_signal_handler)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
