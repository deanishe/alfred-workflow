
.. _api-updates:

Workflow updates
----------------

.. module:: workflow.update

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository.

Currently, only updates from `GitHub releases`_ are supported.

.. important::

    Alfred-Workflow will check for updates, but will neither install them
    nor notify the user that an update is available.


Normally, you would not use :mod:`workflow.update` directly, but use the
corresponding methods on :class:`~workflow.Workflow` and
:class:`~workflow.Workflow3`.

Please see :ref:`guide-updates` in the :ref:`user-manual` for information
on how to enable automatic updates in your workflow.


.. autofunction:: check_update
.. autofunction:: install_update


Helpers
^^^^^^^

.. autoclass:: Version
    :members:

.. autofunction:: download_workflow


.. _GitHub releases: https://help.github.com/categories/85/articles
