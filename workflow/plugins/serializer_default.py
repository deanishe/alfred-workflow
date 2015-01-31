#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-28
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import json
import cPickle
import pickle

from workflow import hooks
from workflow.storage import Serializer


class JSONSerializer(Serializer):
    """Wrapper around :mod:`json`. Sets ``indent`` and ``encoding``.

    Use this serializer if you need readable data files. JSON doesn't
    support Python objects as well as ``cPickle``/``pickle``, so be
    careful which data you try to serialize as JSON.

    """

    name = 'json'

    @staticmethod
    def load(file_obj):
        """Load serialized object from open JSON file.

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from JSON file
        :rtype: object

        """

        return json.load(file_obj)

    @staticmethod
    def dump(obj, file_obj):
        """Serialize object ``obj`` to open JSON file.

        :param obj: Python object to serialize
        :type obj: JSON-serializable data structure
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """

        return json.dump(obj, file_obj, indent=2, encoding='utf-8')


class CPickleSerializer(Serializer):
    """Wrapper around :mod:`cPickle`. Sets ``protocol``.

    This is the default serializer and the best combination of speed and
    flexibility.

    """

    name = 'cpickle'

    @staticmethod
    def load(file_obj):
        """Load serialized object from open pickle file.

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from pickle file
        :rtype: object

        """

        return cPickle.load(file_obj)

    @staticmethod
    def dump(obj, file_obj):
        """Serialize object ``obj`` to open pickle file.

        :param obj: Python object to serialize
        :type obj: Python object
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """

        return cPickle.dump(obj, file_obj, protocol=-1)


class PickleSerializer(Serializer):
    """Wrapper around :mod:`pickle`. Sets ``protocol``.

    Use this serializer if you need to add custom pickling.

    """

    name = 'pickle'

    @staticmethod
    def load(file_obj):
        """Load serialized object from open pickle file.

        .. versionadded:: 1.8

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from pickle file
        :rtype: object

        """

        return pickle.load(file_obj)

    @staticmethod
    def dump(obj, file_obj):
        """Serialize object ``obj`` to open pickle file.

        :param obj: Python object to serialize
        :type obj: Python object
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """

        return pickle.dump(obj, file_obj, protocol=-1)


_serializers = {
    'json': JSONSerializer,
    'cpickle': CPickleSerializer,
    'pickle': PickleSerializer,
}


def get_serializer(name):
    """Return serializer class for ``name``"""
    return _serializers.get(name)


def register():
    """Register plugins"""
    hooks.get_serializer.connect(get_serializer)
