
.. _api-workflow:

Workflow objects
----------------

.. module:: workflow

The :class:`Workflow` object is the main interface to this library.

:class:`Workflow` is targeted at Alfred 2. Use :class:`Workflow3` if
you want to use Alfred 3's new features, such as
:ref:`workflow variables <workflow-variables>` or
:ref:`more powerful modifiers <api-modifiers>`.

See :ref:`setup` in the :ref:`user-manual` for an example of how to set
up your Python script to best utilise the :class:`Workflow` object.


.. autoclass:: Workflow
   :members:


.. _api-settings:

Settings
^^^^^^^^

.. currentmodule:: workflow

:class:`Workflow` and :class:`Workflow3` objects each have a
:attr:`~Workflow.settings` attribute that provides a simple API for storing
workflow settings.

.. autoclass:: workflow.workflow.Settings
  :members:

  .. automethod:: save(self)


.. _api-serializers:

Serializers
^^^^^^^^^^^

.. currentmodule:: workflow.workflow

The serialization API provided by :class:`SerializerManager` is used by
:class:`~workflow.Workflow` to store saved & cached data and settings.
You can register your own serializers on a manager.

The default manager (which supports JSON, pickle and cPickle) is at
:data:`workflow.manager`.

.. autoclass:: SerializerManager
   :members:

.. autoclass:: JSONSerializer
   :members:

.. autoclass:: PickleSerializer
   :members:


.. _api-exceptions:

Exceptions
^^^^^^^^^^

.. currentmodule:: workflow

Alfred-Workflow defines the following exceptions, which may be raised
by the Keychain API.

.. autoexception:: KeychainError

.. autoexception:: PasswordNotFound

.. autoexception:: workflow.workflow.PasswordExists
