
.. _guide-serialization:

===================================
Serialization of stored/cached data
===================================

.. contents::
   :local:

.. currentmodule:: workflow

By default, both cache and data files (created using the APIs described in
:ref:`guide-persistent-data`) are cached using :mod:`cPickle`. This provides
a great compromise in terms of speed and the ability to store arbitrary objects.

When changing or specifying a serializer, use the name under which the
serializer is registered with the :ref:`workflow.manager <managing-serializers>`
object.

.. warning::

    When it comes to cache data, it is *strongly recommended* to stick with the
    default. :mod:`cPickle` is *very* fast and fully supports standard Python
    data structures (``dict``, ``list``, ``tuple``, ``set`` etc.).

    If you really must customise the cache data format, you can change the
    default cache serialization format to :mod:`pickle` thus:

    .. code-block:: python
        :linenos:

        wf = Workflow()
        wf.cache_serializer = 'pickle'

    Unlike the stored data API, the cached data API can't determine the format
    of the cached data. If you change the serializer without clearing the
    cache, errors will probably result as the serializer tries to load data
    in a foreign format.

In the case of stored data, you are free to specify either a global default
serializer or one for each individual datastore:

.. code-block:: python
    :linenos:

    wf = Workflow()
    # Use `pickle` as the global default serializer
    wf.data_serializer = 'pickle'

    # Use the JSON serializer only for these data
    wf.store_data('name', data, serializer='json')

This is primarily so you can create files that are human-readable or useable
by other software. The generated JSON is formatted to make it readable.

The :meth:`stored_data() <workflow.workflow.Workflow.stored_data>` method can
automatically determine the serialization of the stored data (based on the file
extension, which is the same as the name the serializer is registered under),
provided the corresponding serializer is registered. If it isn't, a
:class:`ValueError` will be raised.


Built-in serializers
====================

There are 3 built-in, pre-configured serializers:

- :class:`cpickle <workflow.workflow.CPickleSerializer>` — the default serializer
  for both cached and stored data, with very good support for native Python
  data types;
- :class:`pickle <workflow.workflow.PickleSerializer>` — a more flexible, but
  much slower alternative to ``cpickle``; and
- :class:`json <workflow.workflow.JSONSerializer>` — a very common data format,
  but with limited support for native Python data types.

See the built-in :mod:`cPickle`, :mod:`pickle` and :mod:`json` libraries for
more information on the serialization formats.


.. _managing-serializers:

Managing serializers
====================

You can add your own serializer, or replace the built-in ones, using the
configured instance of :class:`~workflow.SerializerManager` at
``workflow.manager``, e.g. ``from workflow import manager``.

A ``serializer`` object must have ``load()`` and ``dump()`` methods that work
the same way as in the built-in :mod:`json` and :mod:`pickle` libraries, i.e.:

.. code-block:: python
    :linenos:

    # Reading
    obj = serializer.load(open('filename', 'rb'))
    # Writing
    serializer.dump(obj, open('filename', 'w'))

To register a new serializer, call the
:meth:`~workflow.workflow.SerializerManager.register` method of the
``workflow.manager`` object with the name of the serializer and the object
that performs serialization:

.. code-block:: python
   :linenos:
   :emphasize-lines: 14

    from workflow import Workflow, manager


    class MySerializer(object):

        @classmethod
        def load(cls, file_obj):
            # load data from file_obj

        @classmethod
        def dump(cls, obj, file_obj):
            # serialize obj to file_obj

    manager.register('myformat', MySerializer())

.. note::

    The name you specify for your serializer will be the file extension of the
    stored files.


Serializer interface
====================

A serializer **must** conform to this interface (like :mod:`json` and
:mod:`pickle`):

.. code-block:: python
    :linenos:

    serializer.load(file_obj)
    serializer.dump(obj, file_obj)


See the :ref:`api-serializers` section of the API documentation for more
information.
