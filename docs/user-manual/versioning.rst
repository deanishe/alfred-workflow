
.. _manual-versioning:

========================
Versioning and migration
========================

.. versionadded:: 1.10

.. contents::
   :local:


If you intend to distribute your workflow, it's a good idea to use version
numbers. It allows users to see if they're using an out-of-date version, and
more importantly, it allows you to know which version a user has when they
ask you for support or to fix a bug (that you may already have fixed).

If your workflow has a version number set (see :ref:`set-version`), the version
will be logged every time the workflow is run to help with debugging, and can
also be displayed using the ``workflow:version``
:ref:`magic argument <magic-arguments>`.

If you wish to use the :ref:`self-updating feature <manual-updates>`, your
workflow must have a version number.

Having a version number also enables the first run/migration functionality.
See :ref:`first-run` below for details.

.. _set-version:

Setting a version number
========================

There are two ways to set a version number. The simplest and best is to
create a ``version`` file in the root directory of your workflow (next to
``info.plist``) that contains the version number::

	Your Workflow/
		icon.png
		info.plist
		yourscript.py
		version
		workflow/
			...

You may also specify the version number using the ``version`` key in the
``update_settings`` dictionary passed to :class:`~workflow.workflow.Workflow`,
though you can only use this method if your workflow supports self-updates
from GitHub.

Using a ``version`` file is preferable as then you only need to maintain the
version number in one place.


.. _version-numbers:

Version numbers
===============

In version 1.10 and above, Alfred-Workflow requires :ref:`semver`,
which is the format GitHub also expects. Alfred-Workflow deviates from the
semantic versioning standard slightly, most notably in that you don't have to
specify a minor or patch version, i.e. ``1.0`` is fine, as is simply ``1``
(the standard requires these to both be written ``1.0.0``). See
:ref:`semver` for more details on version formatting.

The *de-facto* way to tag releases on GitHub is use a semantic version number
preceded by ``v``, e.g. ``v1.0``, ``v2.3.1`` etc., whereas the *de-facto* way
to version Python libraries is to do the same, but without the preceding ``v``,
e.g. ``1.0``, ``2.3.1`` etc.

As a result, Alfred-Workflow will strip a preceding ``v`` from both local
and remote versions (i.e. you can specify ``1.0`` or ``v1.0`` in either or both
of your Python code and GitHub releases).

When this is done, if the latest GitHub version is higher than the local
version, Alfred-Workflow will consider the remote version to be an update.

Thus, calling :class:`~workflow.workflow.Workflow` with
``update_settings={'version': '1.2', ...}`` or
``update_settings={'version': 'v1.2', ...}`` will be considered the same
version as the GitHub release tag ``v1.2`` or ``1.2`` (or indeed ``1.2.0``).


.. _semver:

Semantic versioning
-------------------

Semantic versioning is a standard for formatting software version numbers.

Essentially, a version number must consist of a major version number, a minor
version number and a patch version number separated by dots, e.g. ``1.0.1``,
``2.10.3`` etc. You should increase the patch version when you fix bugs, the
minor version when you add new features and the major version if you change
the API.

You may also add additional pre-release version info to the end of the version
number, preceded by a hyphen (``-``), e.g. ``2.0.0-rc.1`` or ``2.0.0-beta``.
Note that Alfred-Workflow does not use this pre-release version format to
identify pre-releases; instead the pre-release option on the GitHub release
editing page must be selected for releases that are not production-ready.

Alfred-Workflow differs from the standard in that you aren't required to
specify a minor or patch version, i.e. ``1.0`` is fine, as is ``1`` (and both
are considered equal and also equal to ``1.0.0``).

This change was made as relatively few workflow authors use patch versions.

See the `semantic versioning`_ website for full details of the standard and
the rationale behind it.


.. _first-run:

First run/migration
===================

.. versionadded:: 1.10

If your workflow uses :ref:`version numbers <manual-versioning>`, you can
use the :attr:`Workflow.first_run <workflow.workflow.Workflow.first_run>`
and :attr:`Workflow.last_version_run <workflow.workflow.Workflow.last_version_run>`
attributes to bootstrap newly-installed workflows or to migrate data from
an older version.

:attr:`~workflow.workflow.Workflow.first_run` will be ``True`` if this version
of the workflow has never run before. If an older version has previously run,
:attr:`~workflow.workflow.Workflow.last_version_run` will contain the version
of that workflow.

Both :attr:`~workflow.workflow.Workflow.last_version_run` and
:attr:`~workflow.workflow.Workflow.version` are :class:`~workflow.update.Version`
instances (or ``None``) to make comparison easy. Be sure to check for ``None``
before comparing them: comparing :class:`~workflow.update.Version` and ``None``
will raise a :class:`ValueError`.

:attr:`~workflow.workflow.Workflow.last_version_run` is set to the value of
the currently running workflow if it runs successfully without raising an
exception.

.. important::

	:attr:`~workflow.workflow.Workflow.last_version_run` will only be set
	automatically if you run your workflow via
	:meth:`Workflow.run() <workflow.workflow.Workflow.run>`. This is because
	:class:`~workflow.workflow.Workflow` is often used as a utility class by
	other workflow scripts, and you don't want your background update script
	to confuse things by setting the wrong version.

	If you want to set :attr:`~workflow.workflow.Workflow.last_version_run`
	yourself, use :meth:`~workflow.workflow.Workflow.set_last_version`.



.. _GitHub releases: https://help.github.com/categories/85/articles
.. _semantic versioning: http://semver.org/
