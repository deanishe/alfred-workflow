
.. _api-notify:

Notifications
-------------

.. module:: workflow.notify

.. versionadded:: 1.15

.. note::

    Notifications aren't available in version of macOS older than
    10.8/Mountain Lion. Calling :func:`notify` on these systems will
    silently do nothing.

:mod:`~workflow.notify` allows you to post notifications via macOS's
Notification Center at any time, not just at the end of your script.
Furthermore, it uses your workflow's icon, not Alfred's.

The main API is a single function, :func:`notify`.

It works by copying a simple application to your workflow's data
directory. It replaces the application's icon with your workflow's
icon and then calls the application to post notifications.

.. autofunction:: notify


Helper functions
^^^^^^^^^^^^^^^^

These internal helper functions may also be useful in your workflow.

.. autofunction:: convert_image

.. autofunction:: png_to_icns

.. autofunction:: validate_sound
