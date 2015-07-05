
.. _api-serialization:

Serialization
=============

.. module:: workflow

:class:`Workflow` has
:ref:`several methods for storing persistent data <manual-persistent-data>`
to your workflow's data and cache directories. By default these are stored as
Python :mod:`pickle` objects using :class:`~workflow.CPickleSerializer` (with
the file extension ``.cpickle``).

You may, however, want to serialize your data in a different format, e.g. JSON,
to make it user-readable/-editable or to interface with other software, and
the :class:`~workflow.SerializerManager` and data storage/caching APIs enable
you to do this.

For more information on how to change the default serializers, specify
alternative ones and register new ones, see
:ref:`manual-persistent-data` and :ref:`manual-serialization` in the
:ref:`user-manual`.


API
---

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
