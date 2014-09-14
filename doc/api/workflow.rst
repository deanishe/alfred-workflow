
.. _workflow:

The Workflow Object
===================

.. module:: workflow

.. automodule:: workflow.workflow

.. autoclass:: Workflow
   :members:
   :inherited-members:

.. autoclass:: KeychainError

.. autoclass:: PasswordNotFound

.. autoclass:: PasswordExists



.. _serialization-api:

Serialization
=============

:class:`Workflow` has
:ref:`several methods for storing persistent data <persistent-data>` to your
workflow's data and cache directories. By default these are stored as Python
:mod:`pickle` objects (using :class:`~workflow.workflow.CPickleSerializer`)
(with the file extension ``.pickle``).

You may, however, want to serialize your data in a different format, e.g. JSON,
to make it user-readable/-editable or to interface with other software.

To set the default serializer for cached data,
set :attr:`Workflow.cache_serializer`, and to set the default
serializer for stored data, set :attr:`Workflow.data_serializer`.

.. warning::

    Be careful using ``json``: JSON only supports a subset of Python's
    native data types (e.g., no ``tuple`` or :class:`set`).


There are 3 pre-configured serializers:
:class:`json <workflow.workflow.JSONSerializer>`,
:class:`pickle <workflow.workflow.PickleSerializer>` and
:class:`cpickle <workflow.workflow.CPickleSerializer>`.

The default is :class:`cpickle <workflow.workflow.CPickleSerializer>`, as it
is very fast and can handle most Python objects.

If you need custom pickling behaviour, use the
:class:`pickle <workflow.workflow.PickleSerializer>` serializer instead.

See the built-in :mod:`cPickle`, :mod:`pickle` and :mod:`json`
libraries for more information on the serialization formats.


Adding your own serializer
--------------------------

You can add your own serializer, or replace the built-in ones, using the
configured instance of :class:`~workflow.workflow.SerializerManager` at
``workflow.manager``, e.g. ``from workflow import manager``.

A ``serializer`` object must have ``load()`` and ``dump()`` methods that work
the same way as in the built-in :mod:`json` and :mod:`pickle` libraries, i.e.:

.. code-block:: python
    :linenos:

    # Reading
    obj = serializer.load(open('filename', 'rb'))
    # Writing
    serializer.dump(obj, open('filename', 'wb'))

To register a new serializer, use:

.. code-block:: python
   :linenos:

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

    The name under which you register your serializer will be used as
    the file extension of any saved files.

Cached data is stored in the Workflow's cache directory, which is intended
for temporary and easily regenerated data.

Stored data is stored in the Workflow's data directory, which is intended
for data that is user-generated or not easily recreated.

The default serializer for both cached and stored data is ``cpickle``.

For more information, see :ref:`Persistent data <persistent-data>`.


Serialization classes
---------------------

.. autoclass:: workflow.workflow.SerializerManager
   :members:

.. autoclass:: workflow.workflow.JSONSerializer
   :members:

.. autoclass:: workflow.workflow.CPickleSerializer
   :members:

.. autoclass:: workflow.workflow.PickleSerializer
   :members:

.. .. automodule:: workflow
..     :members:
..     :show-inheritance:
..     :member-order: bysource
