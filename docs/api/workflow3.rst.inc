.. _api-workflow3:

Workflow3 objects
-----------------

.. module:: workflow.workflow3

.. versionadded:: 1.18

:class:`~workflow.Workflow3` is an Alfred 3-only version of
:class:`~workflow.Workflow` that supports Alfred 3's new features.

It supports setting :ref:`workflow-variables` and
:class:`the more advanced modifiers <Modifier>` supported by Alfred 3.

In order for the feedback mechanism to work correctly, it's important
to create :class:`Item3` and :class:`Modifier` objects via the
:meth:`Workflow3.add_item()` and :meth:`Item3.add_modifier()` methods
respectively. If you instantiate :class:`Item3` or :class:`Modifier`
objects directly, the current :class:`Workflow3` object won't be aware
of them, and they won't be sent to Alfred when you call
:meth:`Workflow3.send_feedback()`.

.. autoclass:: workflow.Workflow3
   :members:


.. _api-variables:

Workflow variables
^^^^^^^^^^^^^^^^^^

.. versionadded:: 1.18

Alfred 3 allows you to pass around variables in your workflows. It passes
these to your scripts as environment variables (access them with
:func:`os.getenv`), and you can pass variables back to Alfred via JSON.

In Script Filters, use the ``setvar()`` methods on :class:`Workflow3`,
:class:`Item3` and :class:`Modifier`.

In Run Script actions, use the :class:`Variables`.

See :ref:`workflow-variables` in the User Guide for more information.

:class:`Item3` and :class:`Modifier` are documented below, in the
:ref:`api-modifiers` section.

.. autoclass:: Variables
   :members:


.. _api-modifiers:

Advanced modifiers
^^^^^^^^^^^^^^^^^^

.. versionadded:: 1.18
.. versionchanged:: 1.27

You can specify alternate ``arg``, ``subtitle`` and variables if a
Script Filter result is actioned while holding down a modifier key.

As of Alfred-Workflow version 1.27 and Alfred version 3.4.1, you can also
specify an alternative icon for a modifier.

Add a modifier to an item using :meth:`Item3.add_modifier`, and configure
the :class:`Modifier` via its attributes and :meth:`~Modifier.setvar`
method.

.. autoclass:: Item3
   :members:

.. autoclass:: Modifier
   :members:
