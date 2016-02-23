
.. _api-notifications:

Notifications
=============

.. note::

	Notifications aren't available in version of OS X older than 10.8/Mountain
	Lion. Calling :func:`~workflow.notify.notify` on these systems will
	silently do nothing.

:mod:`~workflow.notify` allows you to post notifications via OS X's
Notification Center at any time, not just at the end of your script.
Furthermore, it uses your workflow's icon, not Alfred's.

The only functions that you should need to use directly to post notifications
are :func:`~workflow.notify.notify` and possibly
:func:`~workflow.notify.validate_sound`.

The image-processing functions :func:`~workflow.notify.convert_image` and
:func:`~workflow.notify.png_to_icns` might be useful outside of this library.

API
---

.. automodule:: workflow.notify
	:members:
