
.. _supported-versions:

==================
Supported versions
==================

Alfred-Workflow supports all versions of Alfred 2–4. It works with Python 3.8
and does not support Python 2 any longer.

Some features are not available on older versions of macOS.

.. contents::
   :local:


Alfred versions
===============

Alfred-Workflow works with all versions of Alfred 2, 3 & 4, but you must
own the `Powerpack`_ to use Alfred's workflow feature.

All Script Filter features provided by Alfred 2 as of v2.8.3 and by Alfred 4 as of v4.0.9 are supported in the latest version of Alfred-Workflow.

The :class:`~workflow.Workflow` class is compatible with Alfred 2+.
The :class:`~workflow.Workflow3` class is only compatible with Alfred 3+.

.. important::

    Versions 3.4.1 altered the way :ref:`workflow variables <workflow-variables>` are set via Script Filter feedback, and :class:`~workflow.Workflow3` as of version 1.27 of Alfred-Workflow uses the new mechanism.

    As a result, versions 1.27+ of Alfred-Workflow are not compatible with versions of Alfred older than 3.4.1.

:class:`~workflow.Workflow3` uses the JSON feedback format in Alfred 3+. It supports :ref:`workflow variables <workflow-variables>` and more advanced modifiers than :class:`~workflow.Workflow`/Alfred 2.


macOS versions
==============

.. warning::

    Versions of macOS before High Sierra have an extremely old version of OpenSSL, which is not compatible with many servers' SSL configurations, including GitHub's. :mod:`workflow.web` cannot connect to these servers, which also means that the `update mechanism <guide-updates>`_ does not work on macOS 10.12/Sierra and older.

Alfred-Workflow supports the same macOS versions as Alfred, namely 10.6 (Snow Leopard) and later (Alfred 3 is 10.9+ only).

.. note::

    :ref:`Notifications`, added in version 1.15 of Alfred-Workflow, are only available on Mountain Lion (10.8) and above.


Python versions
===============

Alfred-Workflow only officially supports the system Pythons that come with macOS (i.e. ``/usr/bin/python3``).

.. important::

    Other Pythons (e.g. Homebrew, conda, pyenv etc.) are *not* supported.

    This is a deliberate design choice, so please do not submit feature requests for support of, or bug reports concerning issues with any non-system Pythons.


.. _include argparse in your workflow: https://pypi.python.org/pypi/argparse
.. _docopt: http://docopt.org/
.. _Powerpack: https://buy.alfredapp.com/
