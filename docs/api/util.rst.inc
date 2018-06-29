
.. _api-util:

Utilities & helpers
-------------------


.. currentmodule:: workflow.util

A collection of functions and classes for common workflow-related tasks, such
as running AppleScript or JXA code, or calling an External Trigger.


.. autofunction:: utf8ify

.. autofunction:: applescriptify

.. autofunction:: run_command

.. autofunction:: run_applescript

.. autofunction:: run_jxa

.. autofunction:: run_trigger

.. autoclass:: AppInfo

.. autofunction:: appinfo


Configuration
^^^^^^^^^^^^^

Functions for manipulating the values of workflow variables in the
`workflow configuration sheet`_/``info.plist``.

.. autofunction:: set_config

.. autofunction:: unset_config


Other helpers
^^^^^^^^^^^^^

These utility classes and functions are used internally by Alfred-Workflow,
but may also be useful in your workflow.

.. autoclass:: LockFile
   :members:

.. autoclass:: uninterruptible
   :members:

.. autofunction:: atomic_writer


.. _api-util-exceptions:


Exceptions
^^^^^^^^^^

The following exceptions, may be raised by utility functions.

.. autoexception:: AcquisitionError

.. autoexception:: subprocess.CalledProcessError


.. _workflow configuration sheet: https://www.alfredapp.com/help/workflows/advanced/variables/#environment
