
.. _serialization:

Serialization
=============

By default, both cache and data files (created using the
:ref:`APIs described above <caching-data>`) are cached using :mod:`cPickle`.
This provides a great compromise in terms of speed and the ability to store
arbitrary objects.

When it comes to cache data, it is *strongly recommended* to stick with
the default. :mod:`cPickle` is *very* fast and fully supports standard Python
data structures (``dict``, ``list``, ``tuple``, ``set`` etc.).

If you need the ability to customise caching, you can change the default
cache serialization format to :mod:`pickle` thus:

.. code-block:: python
    :linenos:

    wf = Workflow()
    wf.cache_serializer = 'pickle'

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
by non-Python programs.

By default, ``cpickle``, ``pickle`` and ``json`` serializers are available.

You can also register your own custom serializers using the
:class:`~workflow.workflow.SerializerManager` interface.

To register a new serializer, call the ``register`` method of the ``workflow.manager``
object:

.. code-block:: python
    :linenos:

    from workflow import Workflow, manager

    wf = Workflow()
    manager.register('myformat', object_with_load_and_dump_methods)

    wf.store_data('name', data, serializer='myformat')

A serializer *must* conform to this interface (like :mod:`json` and :mod:`pickle`):

.. code-block:: python
    :linenos:

    serializer.load(file_obj)
    serializer.dump(obj, file_obj)


.. note::

    The name you use for your serializer will be the file extension of the stored file.

The :meth:`stored_data() <workflow.workflow.Workflow.stored_data>` method can
automatically determine the serialization of the stored data, provided the
corresponding serializer is registered. If it isn't, a ``ValueError`` will be raised.
