#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""Unit tests for serializer classes."""



import os
import sys

import pytest

from workflow.workflow import (
    SerializerManager,
    JSONSerializer,
    PickleSerializer,
    manager as default_manager,
)

# default serializers
SERIALIZERS = ('json', 'pickle')


@pytest.fixture(scope='function')
def manager():
    """Create a `SerializerManager` with the default config."""
    m = SerializerManager()
    m.register('pickle', PickleSerializer)
    m.register('json', JSONSerializer)
    yield m


def is_serializer(obj):
    """Verify that ``obj`` implements serializer API."""
    return hasattr(obj, 'load') and hasattr(obj, 'dump')


def test_default_serializers():
    """Default serializers."""
    for name in SERIALIZERS:
        assert is_serializer(default_manager.serializer(name))

    assert set(SERIALIZERS) == set(default_manager.serializers)


def test_serialization(tempdir, manager):
    """Dump/load data."""
    data = {'arg1': 'value1', 'arg2': 'value2'}

    for name in SERIALIZERS:
        serializer = manager.serializer(name)
        path = os.path.join(tempdir, 'test.{0}'.format(name))
        assert not os.path.exists(path)

        with serializer.atomic_writer(path, 'w') as file_obj:
            serializer.dump(data, file_obj)

        assert os.path.exists(path)

        with open(path, 'rb') as file_obj:
            data2 = serializer.load(file_obj)

        assert data == data2

        os.unlink(path)


def test_register_unregister(manager):
    """Register/unregister serializers."""
    serializers = {}
    for name in SERIALIZERS:
        serializer = manager.serializer(name)
        assert is_serializer(serializer)

    for name in SERIALIZERS:
        serializer = manager.unregister(name)
        assert is_serializer(serializer)
        serializers[name] = serializer

    for name in SERIALIZERS:
        assert manager.serializer(name) is None

    for name in SERIALIZERS:
        with pytest.raises(ValueError):
            manager.unregister(name)

    for name in SERIALIZERS:
        serializer = serializers[name]
        manager.register(name, serializer)


class InvalidSerializer(object):
    """Bad serializer."""


def test_register_invalid(manager):
    """Register invalid serializer."""
    invalid1 = InvalidSerializer()
    invalid2 = InvalidSerializer()
    setattr(invalid2, 'load', lambda x: x)

    with pytest.raises(AttributeError):
        manager.register('bork', invalid1)
    with pytest.raises(AttributeError):
        manager.register('bork', invalid2)


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
