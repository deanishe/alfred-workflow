
.. _notifications:

=============
Notifications
=============

.. versionadded:: 1.15

.. note::

	Notifications are only available on Mountain Lion (10.8) and later. Calling
	:func:`~workflow.notify.notify` on earlier systems will silently fail.

Alfred 2 allows you to post notifications, but only at the end of
a workflow, and only with its own icon.

Alfred-Workflow's :mod:`~workflow.notify` module lets you post notifications
whenever you want, and with your workflow's icon.


Usage
=====

.. code-block:: python
	:linenos:

	from workflow.notify import notify

	notify('My Title', 'My Text')

This is the full API:

.. autofunction:: workflow.notify.notify
    :noindex:

See the :ref:`API documentation <api-notifications>` for details of the other
functions.
