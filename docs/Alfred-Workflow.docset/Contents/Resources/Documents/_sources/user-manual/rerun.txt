
.. _manual-rerun:

==========================
Re-running a Script Filter
==========================

.. versionadded:: 1.23

Alfred 3.2 introduced an new "rerun" feature. Emitting a ``rerun`` value
from a Script Filter tells Alfred to run that script again after the
specified number of seconds. Alfred will also pass back any variables
set at the top-level of your feedback, i.e. via the
:meth:`Workflow3.setvar() <~workflow.workflow3.Workflow3>` method.

Set :attr:`Workflow3.rerun <~workflow.workflow3.Workflow3.rerun>` to instruct
Alfred to re-run your Script Filter.

This could be used, for example, to provide a seamless (to the user) status
update in a workflow that reports on the status of a download client like
`aria2`_ via its API.

The refresh is invisible to the user, as Alfred doesn't update its UI unless
the Script Filter output changes.

In terms of Alfred-Workflow more generally, you might use this feature to
re-run your Script Filter if its data are still being updated in the background.
For example:


.. code-block:: python
    :linenos:

    from workflow import Workflow3
    from workflow.background import is_running, run_in_background

    wf = Workflow3()

    # Unconditionally load data from cache
    data = wf.cached_data('data', ..., max_age=0)

    # Update cached data if they're stale
    if not wf.cached_data_fresh('data', max_age=30):
        run_in_background('update_cache', ...)

    # Tell Alfred to re-run the Script Filter if the cache is
    # currently being updated.
    if is_running('update_cache'):
        wf.rerun = 1

    # Show (stale) cached data
    for d in data:
        wf.add_item(**d)

    wf.send_feedback()


In this way, the results shown to the user will be updated only if the
background update changes the cached data.


.. _aria2: https://aria2.github.io
