# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created 2019-05-05

"""Unit tests for Workflow directory & file APIs."""



import json
import os
import time
from workflow.workflow import BaseSerializer

import pytest

from workflow import manager, Workflow

from .conftest import env, ENV_V4, ENV_V2

_serializer = 'pickle'
_other_serializer = 'json'

def test_directories(alfred4):
    """Workflow directories"""
    data = ENV_V4.get('alfred_workflow_data')
    cache = ENV_V4.get('alfred_workflow_cache')
    wf = Workflow()
    assert wf.datadir == data
    assert os.path.exists(wf.datadir)
    assert wf.cachedir == cache
    assert os.path.exists(wf.cachedir)
    wf.reset()

    # defaults
    with env(alfred_workflow_data=None, alfred_workflow_cache=None):
        data = ENV_V2.get('alfred_workflow_data')
        cache = ENV_V2.get('alfred_workflow_cache')
        wf = Workflow()
        assert wf.datadir == data
        assert os.path.exists(wf.datadir)
        assert wf.cachedir == cache
        assert os.path.exists(wf.cachedir)
        wf.reset()


def test_create_directories(alfred4, tempdir):
    """Workflow creates directories."""
    data = os.path.join(tempdir, 'data')
    cache = os.path.join(tempdir, 'cache')

    assert not os.path.exists(data)
    assert not os.path.exists(cache)

    with env(alfred_workflow_data=data,
             alfred_workflow_cache=cache):
        wf = Workflow()
        assert wf.datadir == data
        assert os.path.exists(data)
        assert wf.cachedir == cache
        assert os.path.exists(cache)
        wf.reset()


def test_cached_data(wf):
    """Cached data stored"""
    data = {'key1': 'value1'}
    d = wf.cached_data('test', lambda: data, max_age=10)
    assert data == d


def test_cached_data_deleted(wf):
    """Cached data deleted"""
    data = {'key1': 'value1'}
    d = wf.cached_data('test', lambda: data, max_age=10)
    assert data == d
    assert wf.cache_data('test', None) is None
    assert not os.path.exists(wf.cachefile(f'test.{_serializer}'))
    # Test alternate code path for non-existent file
    assert wf.cache_data('test', None) is None


def test_delete_all_cache_file(wf):
    """Cached data are all deleted"""
    data = {'key1': 'value1'}
    test_file1 = f'test1.{_serializer}'
    test_file2 = f'test2.{_serializer}'

    wf.cached_data('test1', lambda: data, max_age=10)
    wf.cached_data('test2', lambda: data, max_age=10)
    assert os.path.exists(wf.cachefile(test_file1))
    assert os.path.exists(wf.cachefile(test_file2))
    wf.clear_cache()
    assert not os.path.exists(wf.cachefile(test_file1))
    assert not os.path.exists(wf.cachefile(test_file2))


def test_delete_all_cache_file_with_filter_func(wf):
    """Only part of cached data are deleted"""
    data = {'key1': 'value1'}
    test_file1 = f'test1.{_serializer}'
    test_file2 = f'test2.{_serializer}'

    def filter_func(file):
        if file == test_file1:
            return True
        else:
            return False

    wf.cached_data('test1', lambda: data, max_age=10)
    wf.cached_data('test2', lambda: data, max_age=10)
    assert os.path.exists(wf.cachefile(test_file1))
    assert os.path.exists(wf.cachefile(test_file2))
    wf.clear_cache(filter_func)
    assert not os.path.exists(wf.cachefile(test_file1))
    assert os.path.exists(wf.cachefile(test_file2))
    wf.clear_cache()
    assert not os.path.exists(wf.cachefile(test_file2))


def test_cached_data_callback(wf):
    """Cached data callback"""
    called = {'called': False}
    data = [1, 2, 3]

    def getdata():
        called['called'] = True
        return data

    d = wf.cached_data('test', getdata, max_age=10)
    assert d == data
    assert called['called'] is True


def test_cached_data_no_callback(wf):
    """Cached data no callback"""
    d = wf.cached_data('nonexistent', None)
    assert d is None


def test_cache_expires(wf):
    """Cached data expires"""
    data = ('hello', 'goodbye')
    called = {'called': False}

    def getdata():
        called['called'] = True
        return data

    d = wf.cached_data('test', getdata, max_age=1)
    assert d == data
    assert called['called'] is True
    # should be loaded from cache
    called['called'] = False
    d2 = wf.cached_data('test', getdata, max_age=1)
    assert d2 == data
    assert called['called'] is not True
    # cache has expired
    time.sleep(1)
    # should be loaded from cache (no expiry)
    d3 = wf.cached_data('test', getdata, max_age=0)
    assert d3 == data
    assert called['called'] is not True
    # should hit data func (cached data older than 1 sec)
    d4 = wf.cached_data('test', getdata, max_age=1)
    assert d4 == data
    assert called['called'] is True


def test_cache_fresh(wf):
    """Cached data is fresh"""
    data = 'This is my data'
    d = wf.cached_data('test', lambda: data, max_age=1)
    assert d == data
    assert wf.cached_data_fresh('test', max_age=10)


def test_cache_fresh_non_existent(wf):
    """Non-existent cache data is not fresh"""
    assert not wf.cached_data_fresh('popsicle', max_age=10000)


def test_cache_serializer(wf):
    """Cache serializer"""
    # default
    assert wf.cache_serializer == _serializer
    # unsupported format
    with pytest.raises(ValueError):
        wf.cache_serializer = 'non-existent'
    # default unchanged
    assert wf.cache_serializer == _serializer
    wf.cache_serializer = _other_serializer
    # other built-in
    assert wf.cache_serializer == _other_serializer


def test_alternative_cache_serializer(wf):
    """Alternative cache serializer"""
    data = {'key1': 'value1'}
    assert wf.cache_serializer == _serializer
    wf.cache_data('test', data)
    assert os.path.exists(wf.cachefile(f'test.{_serializer}'))
    assert wf.cached_data('test') == data

    wf.cache_serializer = _other_serializer
    assert wf.cached_data('test') is None
    wf.cache_data('test', data)
    assert os.path.exists(wf.cachefile(f'test.{_other_serializer}'))
    assert wf.cached_data('test') == data


def test_custom_cache_serializer(wf):
    """Custom cache serializer"""
    data = {'key1': 'value1'}

    class MySerializer(BaseSerializer):
        """Simple serializer"""
        is_binary = False

        @classmethod
        def load(self, file_obj):
            return json.load(file_obj)

        @classmethod
        def dump(self, obj, file_obj):
            return json.dump(obj, file_obj, indent=2)

    manager.register('spoons', MySerializer)
    try:
        assert not os.path.exists(wf.cachefile('test.spoons'))
        wf.cache_serializer = 'spoons'
        wf.cache_data('test', data)
        assert os.path.exists(wf.cachefile('test.spoons'))
        assert wf.cached_data('test') == data
    finally:
        manager.unregister('spoons')


def _stored_data_paths(wf, name, serializer):
    """Return list of paths created when storing data"""
    metadata = wf.datafile('.{}.alfred-workflow'.format(name))
    datapath = wf.datafile(name + '.' + serializer)
    return [metadata, datapath]


def test_data_serializer(wf):
    """Data serializer"""
    # default
    assert wf.data_serializer == _serializer
    # unsupported format
    with pytest.raises(ValueError):
        wf.data_serializer = 'non-existent'
    # default unchanged
    assert wf.data_serializer == _serializer
    wf.data_serializer = _other_serializer
    # other built-in
    assert wf.data_serializer == _other_serializer


def test_alternative_data_serializer(wf):
    """Alternative data serializer"""
    data = {'key1': 'value1'}
    assert wf.data_serializer == _serializer
    wf.store_data('test', data)
    for path in _stored_data_paths(wf, 'test', _serializer):
        assert os.path.exists(path)
    assert wf.stored_data('test') == data

    wf.data_serializer = _other_serializer
    assert wf.stored_data('test') == data
    wf.store_data('test', data)
    for path in _stored_data_paths(wf, 'test', _other_serializer):
        assert os.path.exists(path)
    assert wf.stored_data('test') == data

    wf.data_serializer = 'json'
    assert wf.stored_data('test') == data
    wf.store_data('test', data)
    for path in _stored_data_paths(wf, 'test', 'json'):
        assert os.path.exists(path)
    assert wf.stored_data('test') == data


def test_non_existent_stored_data(wf):
    """Non-existent stored data"""
    assert wf.stored_data('banjo magic') is None


def test_borked_stored_data(wf):
    """Borked stored data"""
    data = {'key7': 'value7'}

    wf.store_data('test', data)
    metadata, datapath = _stored_data_paths(wf, 'test', _serializer)
    os.unlink(metadata)
    assert wf.stored_data('test') is None

    wf.store_data('test', data)
    metadata, datapath = _stored_data_paths(wf, 'test', _serializer)
    os.unlink(datapath)
    assert wf.stored_data('test') is None

    wf.store_data('test', data)
    metadata, datapath = _stored_data_paths(wf, 'test', _serializer)
    with open(metadata, 'w') as file_obj:
        file_obj.write('bangers and mash')
        wf.logger.debug('Changed format to `bangers and mash`')
    with pytest.raises(ValueError):
        wf.stored_data('test')


def test_reject_settings(wf):
    """Refuse to overwrite settings.json"""
    data = {'key7': 'value7'}
    wf.data_serializer = 'json'
    with pytest.raises(ValueError):
        wf.store_data('settings', data)


def test_invalid_data_serializer(wf):
    """Invalid data serializer"""
    data = {'key7': 'value7'}
    with pytest.raises(ValueError):
        wf.store_data('test', data, 'spong')


def test_delete_stored_data(wf):
    """Delete stored data"""
    data = {'key7': 'value7'}

    paths = _stored_data_paths(wf, 'test', _serializer)

    wf.store_data('test', data)
    assert wf.stored_data('test') == data
    wf.store_data('test', None)
    assert wf.stored_data('test') is None

    for p in paths:
        assert not os.path.exists(p)


def test_delete_all_stored_data_file(wf):
    """Stored data are all deleted"""
    data = {'key1': 'value1'}
    test_file1 = f'test1.{_serializer}'
    test_file2 = f'test2.{_serializer}'

    wf.store_data('test1', data)
    wf.store_data('test2', data)
    assert os.path.exists(wf.datafile(test_file1))
    assert os.path.exists(wf.datafile(test_file2))
    wf.clear_data()
    assert not os.path.exists(wf.datafile(test_file1))
    assert not os.path.exists(wf.datafile(test_file2))


def test_delete_all_data_file_with_filter_func(wf):
    """Only part of stored data are deleted"""
    data = {'key1': 'value1'}
    test_file1 = f'test1.{_serializer}'
    test_file2 = f'test2.{_serializer}'

    def filter_func(file):
        if file == test_file1:
            return True
        else:
            return False

    wf.store_data('test1', data)
    wf.store_data('test2', data)

    assert os.path.exists(wf.datafile(test_file1))
    assert os.path.exists(wf.datafile(test_file2))
    wf.clear_data(filter_func)
    assert not os.path.exists(wf.datafile(test_file1))
    assert os.path.exists(wf.datafile(test_file2))
    wf.clear_data()
    assert not os.path.exists(wf.datafile(test_file2))
