
.. _background-processes:

Background processes
====================

Many workflows provide a convenient interface to applications and/or web services.

For performance reasons, it's common for workflows to cache data locally, but
updating this cache typically takes a few seconds, making your workflow
unresponsive while an update is occurring, which is very un-Alfred-like.

To avoid such delays, **Alfred-Workflow** provides the :mod:`~workflow.background`
module to allow you to easily run scripts in the background.

There are two functions, :func:`~workflow.background.run_in_background` and
:func:`~workflow.background.is_running`, that provide the interface. The
processes started are proper background daemon processes, so you can start
proper servers as easily as simple scripts.

Here's an example of a common usage pattern (updating cached data in the
background). What we're doing is:

1. Check the age of the cached data and run the update script via
   :func:`~workflow.background.run_in_background` if the cached data are
   too old or don't exist.
2. (Optionally) inform the user that data are being updated.
3. Load the cached data regardless of age.
4. Display the cached data (if any).

..  code-block:: python
    :linenos:

    from workflow import Workflow, ICON_INFO
    from workflow.background import run_in_background, is_running

    def main(wf):
       # Is cache over 6 hours old or non-existent?
       if not wf.cached_data_fresh('exchange-rates', 3600):
           run_in_background('update',
                             ['/usr/bin/python',
                              wf.workflowfile('update_exchange_rates.py')])

       # Add a notification if the script is running
       if is_running('update'):
           wf.add_item('Updating exchange rates...', icon=ICON_INFO)

       exchange_rates = wf.cached_data('exchage-rates')

       # Display (possibly stale) cache data
       if exchange_rates:
           for rate in exchange_rates:
               wf.add_item(rate)

       # Send results to Alfred
       wf.send_feedback()

    if __name__ == '__main__':
       wf = Workflow()
       wf.run(main)

For a working example, see :ref:`Part 2 of the Tutorial <background-updates>` or
the `source code <https://github.com/deanishe/alfred-repos/blob/master/src/repos.py>`_
of my `Git Repos <https://github.com/deanishe/alfred-repos>`_ workflow,
which is a bit smarter about showing the user update information.
