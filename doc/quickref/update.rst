

.. _qr-updates:

Self-Updating
=============

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository
and then asks the user if they want to replace the workflow if a newer version
is available.

Currently, only updates from
`GitHub releases <https://help.github.com/categories/85/articles>`_ are
supported.

For your workflow to be able to recognise and download newer versions, the
``version`` value you pass to :class:`~workflow.workflow.Workflow` **must**
be one of the versions (i.e. tags) in the corresponding GitHub repo's
releases list. There must also be one (and only one) ``.alfredworkflow``
binary attached to the newest release. This is the file that will be downloaded
and installed via Alfred's default installation mechanism.

To use this feature, you must pass a :class:`dict` as the ``update_settings``
argument to :class:`~workflow.workflow.Workflow`. It **must** have the two
keys/values ``github_slug``, which is your username and the name of the
workflow's repo in the format ``username/reponame``, and ``version``, which
is the release version (release tag) of the currently installed version
of the workflow, e.g.:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    ...

    wf = Workflow(..., update_settings={
        # Your username and the workflow's repo's name
        'github_slug': 'username/reponame',
        # The version (i.e. release/tag) of the installed workflow
        'version': 'v1.0',
        # Optional number of days between checks for updates
        'frequency': 7
    }, ...)

    ...

    if wf.update_available:
        wf.start_update()

.. note::

	**Alfred-Workflow** will automatically check in the background if a newer
	version of your workflow is available, but will *not* automatically inform
	the	user nor download and install the update.

To view update status/install a newer version, the user must either
call one of your workflow's Script Filters with the ``workflow:update``
:ref:`magic argument <magic-arguments>`, in which case **Alfred-Workflow**
will handle the update automatically, or you must add your own update action
using :attr:`Workflow.update_available <workflow.workflow.Workflow.update_available>`
and :meth:`Workflow.start_update() <workflow.workflow.Workflow.start_update>`
to check for and install newer versions respectively.

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
