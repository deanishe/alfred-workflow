
.. _background:

Background Tasks
================

.. module:: workflow.background

.. versionadded:: 1.4

Run scripts in the background.

This module allows your workflow to execute longer-running processes, e.g.
updating the data cache from a webservice, in the background, allowing
the workflow to remain responsive in Alfred.

For example, if your workflow requires up-to-date exchange rates, you might
write a script ``update_exchange_rates.py`` to retrieve the data from the
relevant webservice, and call it from your main workflow script:

.. code-block:: python
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

        # max_age=0 will return the cached data regardless of age
        exchange_rates = wf.cached_data('exchage-rates', max_age=0)

        # Display (possibly stale) cached data
        if exchange_rates:
            for rate in exchange_rates:
                wf.add_item(rate)

        # Send results to Alfred
        wf.send_feedback()

    if __name__ == '__main__':
        wf = Workflow()
        wf.run(main)


For a working example, see :ref:`tutorial_2`.

API
---

.. autofunction:: run_in_background

.. autofunction:: is_running
