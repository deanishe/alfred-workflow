
.. _updates:

Self-Updating
=============

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository.

Currently, only updates from
`GitHub releases <https://help.github.com/categories/85/articles>`_
are supported.

.. note::

	Alfred-Workflow will check for updates, but will neither install them nor
	notify the user that an update is available.

Please see :ref:`manual-updates` in the :ref:`user-manual` for information
on how to enable automatic updates in your workflow.

API
---

.. automodule:: workflow.update
    :members:
    :undoc-members:
    :show-inheritance:
