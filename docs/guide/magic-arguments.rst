
.. _magic-arguments:

=================
"Magic" arguments
=================

.. contents::
   :local:


If your Script Filter (or script) accepts a query (or command line arguments),
you can pass it so-called magic arguments that instruct
:class:`~workflow.workflow.Workflow` to perform certain actions, such as
opening the log file or clearing the cache/settings.

These can be a big help while developing and debugging and especially when
debugging problems your Workflow's users may be having.

The :meth:`Workflow.run() <~workflow.workflow.Workflow.run>` method
(which you should "wrap" your Workflow's entry functions in) will catch any
raised exceptions, log them and display them in Alfred. You can call your
Workflow with ``workflow:openlog`` as an Alfred query/command line argument
and :class:`~workflow.workflow.Workflow` will open the Workflow's log file
in the default app (usually **Console.app**).

This makes it easy for you to get at the log file and data and cache directories
(hidden away in ``~/Library``), and for your users to send you their logs
for debugging.

.. note::

    Magic arguments will only work with scripts that accept arguments *and* use
    the :attr:`~workflow.workflow.Workflow.args` property (where magic
    arguments are parsed).

:class:`~workflow.workflow.Workflow` supports the following magic arguments by default:

- ``workflow:magic`` — List available magic arguments.
- ``workflow:help`` — Open workflow's help URL in default web browser. This URL is specified in the ``help_url`` argument to :class:`~workflow.workflow.Workflow`.
- ``workflow:version`` — Display the installed version of the workflow (if one is set).
- ``workflow:delcache`` — Delete the Workflow's cache.
- ``workflow:deldata`` — Delete the Workflow's saved data.
- ``workflow:delsettings`` — Delete the Workflow's settings file (which contains the data stored using :attr:`Workflow.settings <workflow.workflow.Workflow.settings>`).
- ``workflow:foldingdefault`` — Reset diacritic folding to workflow default
- ``workflow:foldingoff`` — Never fold diacritics in search keys
- ``workflow:foldingon`` — Force diacritic folding in search keys (e.g. convert *ü* to *ue*)
- ``workflow:opencache`` — Open the Workflow's cache directory.
- ``workflow:opendata`` — Open the Workflow's data directory.
- ``workflow:openlog`` — Open the Workflow's log file in the default app.
- ``workflow:openterm`` — Open a Terminal window in the Workflow's root directory.
- ``workflow:openworkflow`` — Open the Workflow's root directory (where ``info.plist`` is).
- ``workflow:reset`` — Delete the Workflow's settings, cache and saved data.
- ``workflow:update`` — Check for a newer version of the workflow using GitHub releases and install the newer version if one is available.
- ``workflow:noautoupdate`` — Turn off automatic checks for updates.
- ``workflow:autoupdate`` — Turn automatic checks for updates on.
- ``workflow:prereleases`` — Enable updating the workflow to pre-release versions.
- ``workflow:noprereleases`` — Disable updating the workflow to pre-release versions (default).

The three ``workflow:folding…`` settings allow users to override the diacritic
folding set by a workflow's author. This may be useful if the author's choice
does not correspond with a user's usage pattern.

You can turn off magic arguments by passing ``capture_args=False`` to
:class:`~workflow.workflow.Workflow` on instantiation, or call the corresponding methods of :class:`~workflow.workflow.Workflow` directly,
perhaps assigning your own keywords within your Workflow:

- :meth:`~workflow.workflow.Workflow.open_help`
- :meth:`~workflow.workflow.Workflow.open_log`
- :meth:`~workflow.workflow.Workflow.open_cachedir`
- :meth:`~workflow.workflow.Workflow.open_datadir`
- :meth:`~workflow.workflow.Workflow.open_workflowdir`
- :meth:`~workflow.workflow.Workflow.open_terminal`
- :meth:`~workflow.workflow.Workflow.clear_cache`
- :meth:`~workflow.workflow.Workflow.clear_data`
- :meth:`~workflow.workflow.Workflow.clear_settings`
- :meth:`~workflow.workflow.Workflow.reset` (a shortcut to call the three previous ``clear_*`` methods)
- :meth:`~workflow.workflow.Workflow.check_update`
- :meth:`~workflow.workflow.Workflow.start_update`

.. _custom-magic:

Customising magic arguments
===========================

The default prefix for magic arguments (``workflow:``) is contained in the
:attr:`~workflow.workflow.Workflow.magic_prefix` attribute of
:class:`~workflow.workflow.Workflow`. If you want to change it to, say,
``wf:`` (which will become the default in v2 of Alfred-Workflow), simply
reassign it::

	wf.magic_prefix = 'wf:'

The magic arguments are defined in the :attr:`Workflow.magic_arguments <workflow.workflow.Workflow.magic_arguments>` dictionary.
The dictionary keys are the keywords for the arguments (without the
prefix) and the values are functions that should be called when the magic
argument is entered. You can show a message in Alfred by returning a
``str`` string from the function.

To add a new magic argument that opens the workflow's settings file, you
could do:

.. code-block:: python
	:linenos:

	wf = Workflow()
	wf.magic_prefix = 'wf:'  # Change prefix to `wf:`

	def opensettings():
		subprocess.call(['open', wf.settings_path])
		return 'Opening workflow settings...'

	wf.magic_arguments['settings'] = opensettings

Now entering ``wf:settings`` as your workflow's query in Alfred will
open ``settings.json`` in the default application.
