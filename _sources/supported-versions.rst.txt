
.. _supported-versions:

==================
Supported versions
==================

Alfred-Workflow supports all versions of Alfred 2–4. It works with
Python 2.6 and 2.7, but *not yet* Python 3.

Some features are not available on older versions of macOS.

.. contents::
   :local:


Alfred versions
===============

Alfred-Workflow works with all versions of Alfred 2, 3 & 4, but you must
own the `Powerpack`_ to use Alfred's workflow feature.

All Script Filter features provided by Alfred 2 as of v2.8.3 and by Alfred
4 as of v4.0.2 are supported in the latest version of Alfred-Workflow.

The :class:`~workflow.Workflow` class is compatible with Alfred 2+.
The :class:`~workflow.Workflow3` class is only compatible with Alfred 3+.

.. important::

    Versions 3.4.1 altered the way :ref:`workflow variables <workflow-variables>`
    are set via Script Filter feedback, and :class:`~workflow.Workflow3` as of
    version 1.27 of Alfred-Workflow uses the new mechanism.

    As a result, versions 1.27+ of Alfred-Workflow are not compatible
    with versions of Alfred older than 3.4.1.

:class:`~workflow.Workflow3` uses the JSON feedback format in Alfred 3+.
It supports :ref:`workflow variables <workflow-variables>` and
more advanced modifiers than :class:`~workflow.Workflow`/Alfred 2.


macOS versions
==============

.. warning::

    Versions of macOS before High Sierra have an extremely old version
    of OpenSSL, which is not compatible with many servers' SSL
    configurations, including GitHub's. :mod:`workflow.web` cannot
    connect to these servers, which also means that the
    `update mechanism <guide-updates>`_ does not work on
    macOS 10.12/Sierra and older.

Alfred-Workflow supports the same macOS versions as Alfred,
namely 10.6 (Snow Leopard) and later (Alfred 3 is 10.9+ only).

.. note::

    :ref:`Notifications`, added in version 1.15 of Alfred-Workflow, are
    only available on Mountain Lion (10.8) and above.


Python versions
===============

Alfred-Workflow only officially supports the system Pythons that come with
macOS (i.e. ``/usr/bin/python``), which is 2.6 on 10.6/Snow Leopard and 2.7
on later versions.

.. important::

    Other Pythons (e.g. Homebrew, conda, pyenv etc.) are *not* supported.

    This is a deliberate design choice, so please do not submit feature
    requests for support of, or bug reports concerning issues with any
    non-system Pythons.

    **This includes Python 3**.

    Python 3 support will be added in a new major version of the library
    when it is added to macOS in Catalina.


Here is the `full list of new features in Python 2.7`_, but the
most important things if you want your workflow to run on Snow
Leopard/Python 2.6 are:

- :mod:`argparse` is not available in 2.6. Use :mod:`getopt` or
  `include argparse in your workflow`_. Personally, I'm a big fan of
  `docopt`_ for parsing command-line arguments, but :mod:`argparse`
  is better for certain use cases.
- You must specify field numbers for :meth:`str.format`, i.e.
  ``'{0}.{1}'.format(first, second)`` not just
  ``'{}.{}'.format(first, second)``.
- No :class:`~collections.Counter` or
  :class:`~collections.OrderedDict` in :mod:`collections`.
- No dictionary views in 2.6.
- No set literals.
- No dictionary or set comprehensions.

Python 2.6 is still included in later versions of macOS (up to and
including El Capitan), so run your Python scripts with
``/usr/bin/python2.6`` in addition to ``/usr/bin/python`` (2.7) to
make sure they will run on Snow Leopard.


Why no Python 3 support?
------------------------

Alfred-Workflow is targeted at the system Python on macOS. Its goal is to
enable developers to build workflows that will "just work" for users on any
vanilla installation of macOS since Snow Leopard.

As such, it :ref:`strongly discourages developers <thirdparty>` from
requiring users of their workflows to bugger about with their OS in
order to get a workflow to work. This naturally includes requiring the
installation of some non-default Python.

Python 3 will be supported when it ships with macOS (Catalina),
and never in version 1 of Alfred-Workflow, which must continue to support
Python 2.6 and Alfred 2 (which doesn't get along with Python 3 [1]_).


.. [1] Alfred uses UTF-8, but Alfred 2 doesn't specify an encoding in the
    workflow environment. POSIX-compliant software, like Python, therefore
    assumes ASCII. Python 2 can handle this misconfiguration, but Python 3
    dies in flames.

.. _full list of new features in Python 2.7: https://docs.python.org/3/whatsnew/2.7.html
.. _include argparse in your workflow: https://pypi.python.org/pypi/argparse
.. _docopt: http://docopt.org/
.. _Powerpack: https://buy.alfredapp.com/
