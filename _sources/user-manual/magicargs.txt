
.. _magic-arguments:

"Magic" arguments
=================

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

:class:`~workflow.workflow.Workflow` supports the following magic arguments:

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

The three ``workflow:folding…`` settings allow users to override the diacritic
folding set by a workflow's author. This may be useful if the author's choice
does not correspond with a user's usage pattern.

You can turn off magic arguments by passing ``capture_args=False`` to
:class:`~workflow.workflow.Workflow` on instantiation, or call the corresponding
methods of :class:`~workflow.workflow.Workflow` directly, perhaps assigning your
own keywords within your Workflow:

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
