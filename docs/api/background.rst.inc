
.. _api-background:

Background processes
--------------------

.. module:: workflow.background

.. versionadded:: 1.4

As Alfred may try to run your workflow on every keypress, it's a good idea
to execute longer-running tasks (e.g. fetching data from the a webservice
or application) in a background process.

.. automodule:: workflow.background
   :noindex:

.. autofunction:: run_in_background
.. autofunction:: is_running
.. autofunction:: kill
