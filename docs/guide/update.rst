

.. _guide-updates:

=============
Self-updating
=============

.. module:: workflow.workflow

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub
repository and then asks the user if they want to update the workflow
if a newer version is available.

Currently, only updates from `GitHub releases`_ are supported.


.. contents::
   :local:


GitHub releases
===============

For your workflow to be able to recognise and download newer versions, the
``version`` value you pass to :class:`Workflow` *should*
be one of the versions (i.e. tags) in the corresponding GitHub repo's
releases list. See :ref:`version-numbers` for more information.

There must be **one (and only one)** ``.alfredworkflow`` and/or **one (and only
one)** ``.alfred3workflow`` binary attached to a release otherwise the release
will be ignored. This is the file that will be downloaded and installed via
Alfred's default installation mechanism.

.. important::

    Releases marked as ``pre-release`` on GitHub will be ignored unless the
    ``workflow:prereleases`` :ref:`magic argument <magic-arguments>` has
    been enabled or the ``prereleases`` key is set to ``True`` in the
    ``update_settings`` :class:`dict`.


Supporting Alfred 2 and Alfred 3
--------------------------------

Workflows created *or edited* in Alfred 3 are fundamentally incompatible
with Alfred 2, even if no Alfred 3-only features are used.

If you want to make a new release of an existing workflow that breaks
compatibility with Alfred 2, it's important that you use the alternate
``.alfred3workflow`` file extension for your release binaries to prevent Alfred
2 installations trying to update themselves to death.

You can have both an ``.alfredworkflow`` file and an ``.alfred3workflow`` file
in the same release. If Alfred-Workflow is running under Alfred 3, it will
prefer the ``.alfred3workflow`` if present. Under Alfred 2, or if the release
contains no ``.alfred3workflow`` file, Alfred-Workflow will use the
``.alfredworkflow`` file.

There may only be one file of each type, however, or the release will be
considered invalid.


Configuration
=============

To use self-updating, you must pass a :class:`dict` as the ``update_settings``
argument to :class:`Workflow`. It **must** have the key/value
pair ``github_slug``, which is your username and the name of the
workflow's repo in the format ``username/reponame``. The version number of the currently
installed workflow must also be specified (see below). There are several ways
to specify the version number of your workflow:

1. In Alfred 3, use the Workflow Version field in the workflow
   configuration sheet. This saves the version number in ``info.plist``.
   :class:`Workflow` will retrieve the version from the
   environment variables set by Alfred when it runs your workflow (or by
   parsing ``info.plist`` if not running in Alfred).
2. By setting the ``version`` key in the ``update_settings`` dictionary.
3. By saving a ``version`` file in your workflow's root directory
   (alongside ``info.plist``).


.. _update-example:

Via ``update_settings``:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    __version__ = '1.1'

    ...

    wf = Workflow(..., update_settings={
        # Your username and the workflow's repo's name.
        'github_slug': 'username/reponame',

        # The version (i.e. release/tag) of the installed workflow.
        # If you've set a Workflow Version in Alfred's workflow
        # configuration sheet or if a `version` file exists in
        # the root of your workflow, this key may be omitted
        'version': __version__,

        # Optional number of days between checks for updates.
        'frequency': 7,

        # Force checking for pre-release updates.
        # This is only recommended when distributing a pre-release;
        # otherwise allow users to choose whether they want
        # production-ready or pre-release updates with the
        # `prereleases` magic argument.
        'prereleases': '-beta' in __version__
    }, ...)

    ...

    if wf.update_available:
        # Download new version and tell Alfred to install it
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
        # Download new version and tell Alfred to install it
        wf.start_update()

You **must** use semantic version numbering. Please see
:ref:`guide-versioning` for detailed information on the required version
number format and associated features.

.. note::

	Alfred-Workflow will automatically check in the background if a newer
	version of your workflow is available, but will *not* automatically inform
	the	user nor download and install the update.


Usage
=====

.. note::

    Users can turn off automatic checks for updates with the
    ``workflow:noautoupdate`` :ref:`magic argument <magic-arguments>`
    and back on again with ``workflow:autoupdate``.


You can just leave it up to the user to check update status and install new
versions manually using the ``workflow:update``
:ref:`magic argument <magic-arguments>` in a Script Filter, or you could roll
your own update handling using :attr:`Workflow.update_available` and
:meth:`Workflow.start_update()` to check for and install newer versions
respectively.

The simplest way, however, is usually to add an update notification to the
top of your Script Filter's results that triggers Alfred-Workflow's
``workflow:update`` magic argument:

.. code-block:: python
    :linenos:

    wf = Workflow(...update_settings={...})

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available',
                    'Action this item to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    # Show other results here
    ...

By adding an :class:`Item` with ``valid=False`` and
``autocomplete='workflow:update'``, Alfred's query will be expanded to
``workflow:update`` when a user actions the item, which is a
:ref:`magic argument <magic-arguments>` that will in turn prompt
Alfred-Workflow to download and install the update.


Under the hood
==============

The :meth:`Workflow.check_update` method is called automatically when you
call :meth:`Workflow.run`. If sufficient time has elapsed since the last
check (1 day by default), it starts a background process that checks for
new releases. You can alter the update interval with the optional
``frequency`` key in ``update_settings`` :class:`dict` (see the
:ref:`example above <update-example>`).

:attr:`Workflow.update_available` is ``True`` if an update is available,
and ``False`` otherwise.

:meth:`Workflow.start_update()` returns ``False`` if no update is
available, or if one is, it will return ``True``, then download the
newer version and tell Alfred to install it in the background.

If you want more control over the update mechanism, you can use
:func:`update.check_update() <workflow.update.check_update>` directly.
It caches information on the latest available release under the cache key
``__workflow_update_status``, which you can access via
:meth:`Workflow.cached_data()`.


.. _version-details:

Version numbers
===============

Please see :ref:`guide-versioning` for detailed information on the required
version number format and associated features.


.. _GitHub releases: https://help.github.com/categories/releases/
