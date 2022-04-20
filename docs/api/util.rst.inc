
.. _api-util:

Utility & helper functions
--------------------------


.. currentmodule:: workflow.util

A collection of functions and classes for common workflow-related tasks, such
as running AppleScript or JXA code, or calling an External Trigger.


Scripting
^^^^^^^^^

Functions to simplify running scripts, programs and applications.

.. autofunction:: run_command

.. autofunction:: run_applescript

.. autofunction:: run_jxa

.. autofunction:: run_trigger

.. autoclass:: AppInfo

.. autofunction:: appinfo


Text
^^^^

Text encoding and formatting.

.. autofunction:: unicodify

.. autofunction:: applescriptify


Alfred's API
^^^^^^^^^^^^

Alfred-Workflow provides functions that enable you to call Alfred's AppleScript API directly from Python.


Workflow stuff
""""""""""""""

Manipulate the values of workflow variables in the `workflow configuration sheet`_/``info.plist``.

.. autofunction:: set_config

.. autofunction:: unset_config

Tell Alfred to reload a workflow from disk if it has changed. Normally, Alfred will notice when a workflow changes, but it won't if the workflow's directory is a symlink.

.. autofunction:: reload_workflow


Alfred stuff
""""""""""""

You can open Alfred in normal or file navigation mode:

.. autofunction:: search_in_alfred

.. autofunction:: browse_in_alfred

Or tell Alfred to action one or more files/directories:

.. autofunction:: action_in_alfred

Finally, you can tell Alfred to use a specific theme:

.. autofunction:: set_theme


Miscellaneous
^^^^^^^^^^^^^

These utility classes and functions are used internally by Alfred-Workflow,
but may also be useful in your workflow.


Writing files
"""""""""""""


.. autoclass:: LockFile
   :members:

.. autoclass:: uninterruptible
   :members:

.. autofunction:: atomic_writer


Images & sounds
"""""""""""""""

.. autofunction:: workflow.notify.convert_image

.. autofunction:: workflow.notify.png_to_icns

.. autofunction:: workflow.notify.validate_sound


.. _api-util-exceptions:


Exceptions
^^^^^^^^^^

The following exceptions, may be raised by utility functions.

.. autoexception:: AcquisitionError

.. autoexception:: subprocess.CalledProcessError


.. _workflow configuration sheet: https://www.alfredapp.com/help/workflows/advanced/variables/#environment
