#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-25
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import json
import os
import shutil
import tempfile
import unittest

import pytest

from workflow import storage


DEFAULT_SETTINGS = {'key1': 'value1',
                    'key2': 'hübner'}


########################################################################
# Serializers
########################################################################

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
            self._is_serializer(storage.manager.serializer(name))

        self.assertEqual(set(self.serializers),
                         set(storage.manager.serializers))

    def test_serialization(self):
        """Dump/load data"""
        data = {'arg1': 'value1', 'arg2': 'value2'}

        for name in self.serializers:
            serializer = storage.manager.serializer(name)
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
            serializer = storage.manager.serializer(name)
            self._is_serializer(serializer)

        for name in self.serializers:
            serializer = storage.manager.unregister(name)
            self._is_serializer(serializer)
            serializers[name] = serializer

        for name in self.serializers:
            self.assertEqual(storage.manager.serializer(name), None)

        for name in self.serializers:
            self.assertRaises(ValueError, storage.manager.unregister, name)

        for name in self.serializers:
            serializer = serializers[name]
            storage.manager.register(name, serializer)

    def test_register_invalid(self):
        """Register invalid serializer"""
        class Thing(object):
            """Bad serializer"""
            pass
        invalid1 = Thing()
        invalid2 = Thing()
        setattr(invalid2, 'load', lambda x: x)

        self.assertRaises(AttributeError,
                          storage.manager.register, 'bork', invalid1)
        self.assertRaises(AttributeError,
                          storage.manager.register, 'bork', invalid2)


########################################################################
# PersistentDict
########################################################################

@pytest.fixture
def settings_file(request):
    """pytest fixture for ``settings.json`` file with ``DEFAULT_SETTINGS``

    Create ``settings.json`` file with ``DEFAULT_SETTINGS`` and return
    path to it. Deletes all temporary file on exit.

    """

    tempdir = tempfile.mkdtemp()
    path = os.path.join(tempdir, 'settings.json')

    def tear_down():
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)

    request.addfinalizer(tear_down)

    with open(path, 'wb') as file_obj:
        json.dump(DEFAULT_SETTINGS, file_obj)
    return path


def test_dict_defaults(settings_file):
    """PersistentDict: defaults set correctly"""
    if os.path.exists(settings_file):
        os.unlink(settings_file)
    s = storage.PersistentDict(settings_file, {'key1': 'value2'})
    assert s['key1'] == 'value2'
    s2 = storage.PersistentDict(settings_file)
    assert s2['key1'] == 'value2'


def test_dict_round_trip(settings_file):
    """PersistentDict: items round-trip"""
    if os.path.exists(settings_file):
        os.unlink(settings_file)
    data = {'key1': 'value2'}
    s = storage.PersistentDict(settings_file, data)
    for k, v in data.items():
        assert s[k] == v
    s2 = storage.PersistentDict(settings_file)
    for k, v in data.items():
        assert s2[k] == v


def test_dict_load(settings_file):
    """PersistentDict: load correctly from file"""
    s = storage.PersistentDict(settings_file, {'key1': 'value2'})
    for k in DEFAULT_SETTINGS:
        assert s[k] == DEFAULT_SETTINGS[k]


def test_dict_explicit_save(settings_file):
    """PersistentDict: deep objects require explicit save"""
    s = storage.PersistentDict(settings_file)
    s['key1'] = {'key2': True}
    s2 = storage.PersistentDict(settings_file)
    assert s['key1'] == s2['key1']
    # This should not trigger `PersistentDict.save()`
    s['key1']['key2'] = False
    s3 = storage.PersistentDict(settings_file)
    assert s['key1'] != s3['key1']
    # Should work after explicit dave
    s.save()
    s4 = storage.PersistentDict(settings_file)
    assert s['key1'] == s4['key1']


def test_dict_methods(settings_file):
    """PersistentDict: dict methods"""
    other = {'key1': 'spoons!'}
    s = storage.PersistentDict(settings_file)
    assert s['key1'] == DEFAULT_SETTINGS['key1']
    s.update(other)
    s.setdefault('key3', [])
    s2 = storage.PersistentDict(settings_file)
    assert s['key1'] == s2['key1']
    assert s['key1'] == other['key1']
    assert s2['key3'] == []
    # Delete item
    del s['key1']
    s3 = storage.PersistentDict(settings_file)
    assert 'key1' not in s3


########################################################################
# ???
########################################################################

if __name__ == '__main__':
    pytest.main([__file__])
