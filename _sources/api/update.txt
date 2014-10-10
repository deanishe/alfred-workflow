
.. _updates:

Self-Updating
=============

.. module:: workflow.update

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository
and then asks the user if they want to replace the workflow if a newer version
is available.

Currently, only updates from
`GitHub releases <https://help.github.com/categories/85/articles>`_ are
supported.

Please see :ref:`manual-updates` in the :ref:`user-manual` for information on how
to enable automatic updates.

API
---

.. automodule:: workflow.update
    :members:
    :undoc-members:
    :show-inheritance:
