
.. _supported-versions:

==================
Supported software
==================

.. contents::
   :local:


Alfred versions
===============

Alfred-Workflow works with all versions of Alfred 2 and 3, but you must own the
`Powerpack`_ to use Alfred's workflow feature.

All Script Filter features provided by Alfred 2 as of v2.8.3 and by Alfred 3
as of v3.1 are supported in the latest version of Alfred-Workflow.

The :class:`~workflow.workflow.Workflow` class is compatible with both Alfred 2
and Alfred 3. The :class:`~workflow.workflow3.Workflow3` class is only
compatible with Alfred 3.

:class:`~workflow.workflow3.Workflow3` uses Alfred 3's JSON feedback format.
It supports :ref:`workflow variables <workflow-variables>` and more advanced
modifiers than :class:`~workflow.workflow.Workflow`/Alfred 2.


OS X versions
=============

Alfred-Workflow supports the same OS X versions as Alfred 2 and 3,
namely 10.6 (Snow Leopard) and later (Alfred 3 is 10.9+ only).

.. note::

    :ref:`Notifications`, added in version 1.15 of Alfred-Workflow, are only
    available on Mountain Lion (10.8) and above.


Python versions
===============

Alfred-Workflow only supports the system Pythons that come with OS X
(i.e. ``/usr/bin/python``), which is 2.6 on 10.6/Snow Leopard and 2.7
on later versions.

.. important::
    Other Pythons (e.g. Homebrew, conda, pyenv etc.) are *not* supported.

    This is a deliberate design choice, so please do not submit feature
    requests for support of, or bug reports concerning issues with any
    non-system Pythons.

    **This includes Python 3**.

    (But if you manage to add full Python 3 support without breaking
    2.6, a pull request would be gratefully accepted.)


Here is the `full list of new features in Python 2.7`_, but the
most important things if you want your workflow to run on Snow
Leopard/Python 2.6 are:

- :mod:`argparse` is not available in 2.6. Use :mod:`getopt` or
  `include argparse in your workflow`_. Personally, I'm a big fan of
  `docopt`_ for parsing command-line arguments, but :mod:`argparse` is better
  for certain use cases.
- You must specify field numbers for :meth:`str.format`, i.e.
  ``'{0}.{1}'.format(first, second)`` not just
  ``'{}.{}'.format(first, second)``.
- No :class:`~collections.Counter` or
  :class:`~collections.OrderedDict` in :mod:`collections`.
- No dictionary views in 2.6.
- No set literals.
- No dictionary or set comprehensions.

Python 2.6 is still included in later versions of OS X (up to and including El
Capitan), so run your Python scripts with ``/usr/bin/python2.6`` in addition to
``/usr/bin/python`` (2.7) to make sure they will run on Snow Leopard.


Why no Python 3 support?
------------------------

Alfred-Workflow is targeted at the system Python on OS X. It's goal is to
enable developers to build workflows that will "just work" for users on any
vanilla installation of OS X since Snow Leopard.

As such, it :ref:`strongly discourages developers <thirdparty>` from requiring
users of their workflows to bugger about with their OSes in order to get a
workflow to work. This naturally includes requiring the installation of some
non-default Python.

Alfred-Workflow is also precisely the kind of project that's hard to make 2-
and 3-compatible. Python 2.6 support is a hard requirement.
:mod:`workflow.web`, as an HTTP library, is all about working with strings of
non-specific encoding, which Python 3 `deliberately turned into a complete shit
show`_ (though it's slowly getting better).

I don't use Python 3 (when I can avoid it), and it's not part of OS X, so I
consider the huge effort required to write 2.6- and 3.x-compatible code a waste
of *my* time. If someone else wants to contribute Python 3 support, it will be
gratefully accepted.

I realise that Python 3 solves many of the string-handling issues that
catch out novice Pythonistas, but as stated, support for non-system
Pythons is simply not a goal of this project.

Python 3 will be supported when it ships with OS X by default, and never
in version 1 of Alfred-Workflow, which must continue to support Python 2.6
and Alfred 2 (which doesn't get along with Python 3 [1]_).


.. [1] Alfred 2 doesn't specify an encoding in the workflow environment, so
    Python 3 goes all POSIX and assumes ASCII, not UTF-8, and therefore
    dies in flames.

.. _full list of new features in Python 2.7: https://docs.python.org/3/whatsnew/2.7.html
.. _include argparse in your workflow: https://pypi.python.org/pypi/argparse
.. _docopt: http://docopt.org/
.. _Powerpack: https://buy.alfredapp.com/
.. _deliberately turned into a complete shit show: http://lucumr.pocoo.org/2014/1/5/unicode-in-2-and-3/
