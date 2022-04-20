
.. _background-processes:

====================
Background processes
====================

.. currentmodule:: workflow.background

Many workflows provide a convenient interface to applications and/or web services.

For performance reasons, it's common for workflows to cache data locally, but
updating this cache typically takes a few seconds, making your workflow
unresponsive while an update is occurring, which is very un-Alfred-like.

To avoid such delays, Alfred-Workflow provides the :mod:`~workflow.background`
module to allow you to easily run scripts in the background.

There are two functions, :func:`run_in_background` and :func:`is_running`,
that provide the main interface. The processes started are full daemon
processes, so you can start real servers as easily as simple scripts.

Here's an example of a common usage pattern (updating cached data in the
background). What we're doing is:

1. Checking the age of the cached data and running the update script via
   :func:`run_in_background` if the cached data are too old or don't exist.
2. (Optionally) informing the user that data are being updated.
3. Loading the cached data regardless of age.
4. Displaying the cached data (if any).

.. code-block:: python
   :linenos:

    from workflow import Workflow3, ICON_INFO
    from workflow.background import run_in_background, is_running

    def main(wf):
        # Is cache over 1 hour old or non-existent?
        if not wf.cached_data_fresh('exchange-rates', 3600):
            run_in_background('update',
                              ['/usr/bin/python3',
                               wf.workflowfile('update_exchange_rates.py')])

        if is_running('update'):
            # Tell Alfred to run the script again every 0.5 seconds
            # until the `update` job is complete (and Alfred is
            # showing results based on the newly-retrieved data)
            wf.rerun = 0.5
            # Add a notification if the script is running
            wf.add_item('Updating exchange rates...', icon=ICON_INFO)

        # max_age=0 will load any cached data regardless of age
        exchange_rates = wf.cached_data('exchage-rates', max_age=0)

        # Display (possibly stale) cache data
        if exchange_rates:
            for rate in exchange_rates:
                wf.add_item(rate)

        # Send results to Alfred
        wf.send_feedback()

    if __name__ == '__main__':
       # Use Workflow3 so we can use Alfred 3's awesome `rerun` feature
       wf = Workflow3()
       wf.run(main)


For a working example, see
:ref:`Part 2 of the Tutorial <background-updates>` or the
`source code <https://github.com/deanishe/alfred-repos/blob/88b6128a2a9214412d26707d09e65875b1964918/src/repos.py#L409>`_
of my `Git Repos <https://github.com/deanishe/alfred-repos>`_ workflow,
which is a bit smarter about showing the user update information.
