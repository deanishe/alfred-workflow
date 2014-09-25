

.. _manual-updates:

Self-Updating
=============

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository
and then asks the user if they want to replace the workflow if a newer version
is available.

.. danger::

    If you are not careful, you might accidentally overwrite a local version of
    the worklow you're working on and lose all your changes!

    If you're working on a workflow, it's a good idea to make sure you increase
    the version number *before* you start making any changes.

    See :ref:`version-numbers` for precise information on how
    **Alfred-Workflow** determines whether a workflow has been updated.


Currently, only updates from `GitHub releases`_ are supported.

For your workflow to be able to recognise and download newer versions, the
``version`` value you pass to :class:`~workflow.workflow.Workflow` **should**
be one of the versions (i.e. tags) in the corresponding GitHub repo's
releases list. See :ref:`version-numbers` for more information.

There must also be one (and only one) ``.alfredworkflow`` binary attached to a
release otherwise it will be ignored. This is the file that will be downloaded
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

    __version__ = '1.1'

    ...

    wf = Workflow(..., update_settings={
        # Your username and the workflow's repo's name
        'github_slug': 'username/reponame',
        # The version (i.e. release/tag) of the installed workflow
        'version': __version__,
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



.. _version-numbers:

Version numbers
---------------

Currently, **Alfred-Workflow** is not particularly smart when it comes to
version numbers. This may change in the future but will require imposing a
specific format for version numbers on workflow authors. If that does happen,
it will be `semantic versioning`_, which you should probably be using anyway.

The *de-facto* way to tag releases on GitHub is use a semantic version number
preceded by ``v``, e.g. ``v1.0``, ``v2.3.1`` etc., whereas the *de-facto* way
to version Python libraries is to do the same, but without the preceding ``v``,
e.g. ``1.0``, ``2.3.1`` etc.

As a result, **Alfred-Workflow** will strip a preceding ``v`` from both local
and remote versions (i.e. you can specify ``1.0`` or ``v1.0`` either or both
in your Python code and GitHub releases).

When this is done, if the latest GitHub version is not the same as the local
version, **Alfred-Workflow** will consider the remote version to be an update.
**No further comparison of versions takes place**.

Thus, calling :class:`~workflow.workflow.Workflow` with
``update_settings={'version': '1.2', ...}`` or
``update_settings={'version': 'v1.2', ...}`` will be considered the same
version as the GitHub release tag ``v1.2`` or ``1.2``.

.. danger::

    If the local and GitHub version differ *in any other way* than starting
    with ``v``, the GitHub version will be considered an update.


.. _GitHub releases: https://help.github.com/categories/85/articles
.. _semantic versioning: http://semver.org/
