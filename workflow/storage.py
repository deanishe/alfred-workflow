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

from workflow import env, hooks, plugins


def get_serializer(name, **kwargs):
    """Return serializer class for ``name``

    Returns ``None`` if no serializer could be found.

    :param name: Name of serializer to retrieve
    :type name: string
    :param **kwargs: Passed to ``__init__`` method of serializer class
    :returns: instance of subclass of :class:`Serializer` or ``None``

    """

    if not len(plugins.get_plugins()):  # Plugins not initialised yet
        plugins.init_plugins()

    cls = hooks.get_serializer.first_response(name)
    log.debug('{0} serializer for {1}'.format(cls.__name__, name))

    if cls is not None:
        return cls(**kwargs)

    return None


class Serializer(object):
    """Base class for serializers

    This class implements the full data storage/caching API but
    the :meth:`dump` and :meth:`load` are stubs that must be overridden
    by subclasses (concrete serializers).

    Any object that has ``dump()`` and ``load()`` methods (and a ``name``
    attribute) that follow the standard Python API (e.g., :mod:`json`
    or :mod:`pickle`) can be a serializer. It needn't inherit from this
    class but must then implement the full API:

    - ``dump()``
    - ``load()``
    - ``cache_data()``
    - ``cached_data()``
    - ``store_data()``
    - ``stored_data()``

    """

    def __init__(self):
        #: In subclasses, name **must** be set.
        #: It is the format the serializer can handle and also the file
        #: extension of saved files.
        self.name = None
        self._filepath = None

    @property
    def filepath(self):
        """The path the current file will be written to.

        Will only be set when one of the store/load methods is called.

        """

        return self._filepath

    def _get_paths(self, name):
        """Return ``(filepath, metadata_path)``"""
        filename = '{0}.{1}'.format(self.name)
        filepath = os.path.join(env.datadir, filename)
        metadata_name = '.{0}.aw-meta'.format(self.name)
        metadata_path = os.path.join(env.datadir, metadata_name)

        return (filepath, metadata_path)

    def store_data(self, name, data, **kwargs):
        """Save data to data directory

        If ``data`` is ``None``, datastore will be deleted.

        """

        filepath, metadata_path = self._get_paths(name)
        self._filepath = filepath

        try:
            if data is None:  # Delete stored data
                for path in (filepath, metadata_path):
                    if os.path.exists(path):
                        os.unlink(path)
                        log.debug('Deleted data file : {0}'.format(path))
            else:
                # Save file extension
                with open(metadata_path, 'wb') as fp:
                    fp.write(self.name)

                with open(filepath, 'wb') as fp:
                    self.dump(data, fp)

                log.debug('Stored data saved to : {0}'.format(filepath))
        finally:
            self._filepath = None

    def stored_data(self, name, **kwargs):
        """Load data stored under ``name`` from data directory.

        Returns ``None`` if datastore is not found.

        :param name: Name of datastore

        """

    def cached_data(self, name, data_func=None, max_age=0, **kwargs):
        """Retrieve data from cache or re-generate and re-cache data if
        stale/non-existant. If ``max_age`` is 0 (default), return cached
        data no matter how old.

        """

    def cache_data(self, name, data, **kwargs):
        """Save ``data`` to cache under ``name``.

        If ``data`` is ``None``, the corresponding cache file will be
        deleted.

        """

    def load(self, file_obj, **kwargs):
        """Return data deserialized from ``file_obj``"""
        raise NotImplementedError

    def dump(self, data, file_obj, **kwargs):
        """Serialize ``data`` to ``file_obj``"""
        raise NotImplementedError


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
