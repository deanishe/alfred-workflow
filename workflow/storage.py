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

import cPickle
import json
import os
import pickle


class PersistentDict(dict):
    """A dictionary that saves itself when changed.

    Dictionary keys & values will be saved as a JSON file at
    ``filepath``. If the file does not exist, the dictionary (and
    settings file) will be initialised with ``defaults``.

    :param filepath: where to save the settings
    :type filepath: :class:`unicode`
    :param defaults: dict of default settings
    :type defaults: :class:`dict`


    An appropriate instance is provided by :class:`~workflow.Workflow`
    instances at :attr:`<Workflow.settings> workflow.Workflow.settings`.

    """

    def __init__(self, filepath, defaults=None):

        super(PersistentDict, self).__init__()
        self._filepath = filepath
        self._nosave = False
        if os.path.exists(self._filepath):
            self._load()
        elif defaults:
            for key, val in defaults.items():
                self[key] = val
            self.save()  # save default settings

    def _load(self):
        """Load cached settings from JSON file `self._filepath`"""

        self._nosave = True
        with open(self._filepath, 'rb') as file_obj:
            for key, value in json.load(file_obj, encoding='utf-8').items():
                self[key] = value
        self._nosave = False

    def save(self):
        """Save settings to JSON file specified in ``self._filepath``

        If you're using this class via :attr:`Workflow.settings`, which
        you probably are, ``self._filepath`` will be ``settings.json``
        in your workflow's data directory (see :attr:`~Workflow.datadir`).
        """
        if self._nosave:
            return
        data = {}
        for key, value in self.items():
            data[key] = value
        with open(self._filepath, 'wb') as file_obj:
            json.dump(data, file_obj, sort_keys=True, indent=2,
                      encoding='utf-8')

    # dict methods
    def __setitem__(self, key, value):
        super(PersistentDict, self).__setitem__(key, value)
        self.save()

    def __delitem__(self, key):
        super(PersistentDict, self).__delitem__(key)
        self.save()

    def update(self, *args, **kwargs):
        """Override :class:`dict` method to save on update."""
        super(PersistentDict, self).update(*args, **kwargs)
        self.save()

    def setdefault(self, key, value=None):
        """Override :class:`dict` method to save on update."""
        ret = super(PersistentDict, self).setdefault(key, value)
        self.save()
        return ret

    def clear(self):
        """Override :class:`dict` method to save on update."""
        ret = super(PersistentDict, self).clear()
        self.save()
        return ret

    def pop(self, *args):
        """Override :class:`dict` method to save on update."""
        ret = super(PersistentDict, self).pop(*args)
        self.save()
        return ret

    def popitem(self):
        """Override :class:`dict` method to save on update."""
        ret = super(PersistentDict, self).popitem()
        self.save()
        return ret


class SerializerManager(object):
    """Contains registered serializers.

    .. versionadded:: 1.8

    A configured instance of this class is available at
    ``workflow.manager``.

    Use :meth:`register()` to register new (or replace
    existing) serializers, which you can specify by name when calling
    :class:`Workflow` data storage methods.

    See :ref:`manual-serialization` and :ref:`manual-persistent-data`
    for further information.

    """

    def __init__(self):
        self._serializers = {}

    def register(self, name, serializer):
        """Register ``serializer`` object under ``name``.

        Raises :class:`AttributeError` if ``serializer`` in invalid.

        .. note::

            ``name`` will be used as the file extension of the saved files.

        :param name: Name to register ``serializer`` under
        :type name: ``unicode`` or ``str``
        :param serializer: object with ``load()`` and ``dump()``
            methods

        """

        # Basic validation
        getattr(serializer, 'load')
        getattr(serializer, 'dump')

        self._serializers[name] = serializer

    def serializer(self, name):
        """Return serializer object for ``name`` or ``None`` if no such
        serializer is registered

        :param name: Name of serializer to return
        :type name: ``unicode`` or ``str``
        :returns: serializer object or ``None``

        """

        return self._serializers.get(name)

    def unregister(self, name):
        """Remove registered serializer with ``name``

        Raises a :class:`ValueError` if there is no such registered
        serializer.

        :param name: Name of serializer to remove
        :type name: ``unicode`` or ``str``
        :returns: serializer object

        """

        if name not in self._serializers:
            raise ValueError('No such serializer registered : {0}'.format(name))

        serializer = self._serializers[name]
        del self._serializers[name]

        return serializer

    @property
    def serializers(self):
        """Return names of registered serializers"""
        return sorted(self._serializers.keys())


class JSONSerializer(object):
    """Wrapper around :mod:`json`. Sets ``indent`` and ``encoding``.

    .. versionadded:: 1.8

    Use this serializer if you need readable data files. JSON doesn't
    support Python objects as well as ``cPickle``/``pickle``, so be
    careful which data you try to serialize as JSON.

    """

    @classmethod
    def load(cls, file_obj):
        """Load serialized object from open JSON file.

        .. versionadded:: 1.8

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from JSON file
        :rtype: object

        """

        return json.load(file_obj)

    @classmethod
    def dump(cls, obj, file_obj):
        """Serialize object ``obj`` to open JSON file.

        .. versionadded:: 1.8

        :param obj: Python object to serialize
        :type obj: JSON-serializable data structure
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """

        return json.dump(obj, file_obj, indent=2, encoding='utf-8')


class CPickleSerializer(object):
    """Wrapper around :mod:`cPickle`. Sets ``protocol``.

    .. versionadded:: 1.8

    This is the default serializer and the best combination of speed and
    flexibility.

    """

    @classmethod
    def load(cls, file_obj):
        """Load serialized object from open pickle file.

        .. versionadded:: 1.8

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from pickle file
        :rtype: object

        """

        return cPickle.load(file_obj)

    @classmethod
    def dump(cls, obj, file_obj):
        """Serialize object ``obj`` to open pickle file.

        .. versionadded:: 1.8

        :param obj: Python object to serialize
        :type obj: Python object
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """

        return cPickle.dump(obj, file_obj, protocol=-1)


class PickleSerializer(object):
    """Wrapper around :mod:`pickle`. Sets ``protocol``.

    .. versionadded:: 1.8

    Use this serializer if you need to add custom pickling.

    """

    @classmethod
    def load(cls, file_obj):
        """Load serialized object from open pickle file.

        .. versionadded:: 1.8

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from pickle file
        :rtype: object

        """

        return pickle.load(file_obj)

    @classmethod
    def dump(cls, obj, file_obj):
        """Serialize object ``obj`` to open pickle file.

        .. versionadded:: 1.8

        :param obj: Python object to serialize
        :type obj: Python object
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """

        return pickle.dump(obj, file_obj, protocol=-1)


# Set up default manager and register built-in serializers
manager = SerializerManager()
manager.register('cpickle', CPickleSerializer)
manager.register('pickle', PickleSerializer)
manager.register('json', JSONSerializer)
