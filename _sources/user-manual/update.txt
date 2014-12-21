

.. _manual-updates:

=============
Self-updating
=============

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository
and then asks the user if they want to replace the workflow if a newer version
is available.

Users may turn off automatic checks for updates using the
``workflow:noautoupdate`` :ref:`magic argument <magic-arguments>`.

.. danger::

    If you are not careful, you might accidentally overwrite a local version of
    the worklow you're working on and lose all your changes!

    If you're working on a workflow, it's a good idea to make sure you increase
    the version number *before* you start making any changes.

    See :ref:`version-numbers` for precise information on how
    Alfred-Workflow determines whether a workflow has been updated.


Currently, only updates from `GitHub releases`_ are supported.

For your workflow to be able to recognise and download newer versions, the
``version`` value you pass to :class:`~workflow.workflow.Workflow` **should**
be one of the versions (i.e. tags) in the corresponding GitHub repo's
releases list. See :ref:`version-numbers` for more information.

There must be one (and only one) ``.alfredworkflow`` binary attached to a
release otherwise it will be ignored. This is the file that will be downloaded
and installed via Alfred's default installation mechanism.

.. important::

    Releases marked as ``pre-release`` on GitHub will also be ignored.

To use this feature, you must pass a :class:`dict` as the ``update_settings``
argument to :class:`~workflow.workflow.Workflow`. It **must** have the key/value
pair ``github_slug``, which is your username and the name of the
workflow's repo in the format ``username/reponame``. The version of the currently
installed workflow must also be specified. You can do this in the
``update_settings`` dict or in a ``version`` file in the root of your workflow
(next to ``info.plist``), e.g.:

.. _update-example:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    __version__ = '1.1'

    ...

    wf = Workflow(..., update_settings={
        # Your username and the workflow's repo's name
        'github_slug': 'username/reponame',
        # The version (i.e. release/tag) of the installed workflow
        # If a `version` file exists in the root of your workflow,
        # this key may be omitted
        'version': __version__,
        # Optional number of days between checks for updates
        'frequency': 7
    }, ...)

    ...

    if wf.update_available:
        wf.start_update()

Or alternatively, create a ``version`` file in the root directory or your
workflow alongside ``info.plist``::

    Your Workflow/
        icon.png
        info.plist
        yourscript.py
        version
        workflow/
            ...
            ...


The ``version`` file should be plain text with no file extension and contain
nothing but the version string, e.g.::

    1.2.5


Using a ``version`` file:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    ...

    wf = Workflow(..., update_settings={
        # Your username and the workflow's repo's name
        'github_slug': 'username/reponame',
        # Optional number of days between checks for updates
        'frequency': 7
    }, ...)

    ...

    if wf.update_available:
        wf.start_update()

Please see :ref:`manual-versioning` for detailed information on the required
version number format and associated features.

.. note::

	Alfred-Workflow will automatically check in the background if a newer
	version of your workflow is available, but will *not* automatically inform
	the	user nor download and install the update.

To view update status/install a newer version, the user must either
call one of your workflow's Script Filters with the ``workflow:update``
:ref:`magic argument <magic-arguments>`, in which case Alfred-Workflow
will handle the update automatically, or you must add your own update action
using :attr:`Workflow.update_available <workflow.workflow.Workflow.update_available>`
and :meth:`Workflow.start_update() <workflow.workflow.Workflow.start_update>`
to check for and install newer versions respectively.

The :meth:`~workflow.workflow.Workflow.check_update` method is called
automatically when you create a :class:`workflow.workflow.Workflow` object. If
sufficient time has elapsed since the last check (1 day by default), it starts
a background process that checks for new releases. You can alter the update
interval with the optional ``frequency`` key in ``update_settings``
:class:`dict` (see the :ref:`example above <update-example>`).

:attr:`Workflow.update_available <workflow.workflow.Workflow.update_available>`
is ``True`` if an update is available, and ``False`` otherwise.

:meth:`Workflow.start_update() <workflow.workflow.Workflow.start_update>`
returns ``False`` if no update is available, or if one is, it will return
``True``, download the newer version and tell Alfred to install it.

If you want more control over the update mechanism, you can use
:func:`update.check_update() <workflow.update.check_update>` directly.
It caches information on the latest available release under the cache key
``__workflow_update_status``, which you can access via
:meth:`Workflow.cached_data() <workflow.workflow.Workflow.cached_data>`.

Users can turn off automatic checks for updates with the ``workflow:noautoupdate``
:ref:`magic argument <magic-arguments>` and back on again with ``workflow:autoupdate``.


Version numbers
===============

Please see :ref:`manual-versioning` for detailed information on the required
version number format and associated features.


.. _GitHub releases: https://help.github.com/categories/85/articles
