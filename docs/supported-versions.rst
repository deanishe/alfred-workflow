
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

All Script Filter features provided by Alfred 2 as of v2.8.3 are supported
in the latest version of Alfred-Workflow.

New features introduced in Alfred 3, such as more powerful modifiers, will
be supported by Alfred-Workflow 2.


OS X versions
=============

Alfred-Workflow supports the same OS X versions as Alfred 2, namely 10.6 (Snow
Leopard) and later.

.. note::

    :ref:`Notifications`, added in version 1.15 of Alfred-Workflow, are only
    available on Mountain Lion (10.8) and above.


Python versions
===============

Alfred-Workflow supports versions 2.6 and 2.7 of Python. Python 3 is *not*
supported.

Alfred-Workflow is intended to run on the OS X default system Python
(``/usr/bin/python``), which is version 2.6 on OS X 10.6 and 2.7 on all later
versions.

Here is the `full list of new features in Python 2.7`_, but the
most important things if you want your workflow to run on Snow
Leopard/Python 2.6 are:

- :mod:`argparse` is not available in 2.6. Use :mod:`getopt` or
  `include argparse in your workflow`_. Personally, I'm a big fan of
  `docopt`_ for parsing command-line arguments, but :mod:`argparse` is better
  for certain use cases.
- No dictionary views in 2.6.
- No set literals.
- No dictionary or set comprehensions.
- You must specify field numbers for :meth:`str.format`, i.e.
  ``'{0}.{1}'.format(first, second)`` not just
  ``'{}.{}'.format(first, second)``.
- No :class:`~collections.Counter` or
  :class:`~collections.OrderedDict` in :mod:`collections`.

Python 2.6 is still included in later versions of OS X (up to and including
Yosemite), so run your Python scripts with ``/usr/bin/python2.6`` in addition to
``/usr/bin/python`` (2.7) to make sure they will run on Snow Leopard.


Why no Python 3 support?
------------------------

Three main reasons:

1. Python 3 isn't installed by default on any version of OS X.
2. Python 3 doesn't get along well with Alfred 2.
3. Alfred-Workflow is precisely the kind of project that's hard to make
   2- and 3-compatible.

Bluntly put, because of **3**, Python 3 support won't come until **1** and/or
**2** changes.

Python 3 is *awesome* for writing workflows in theory. The encoding errors
that are such a pain in Python 2 mostly just disappear.

In practice, Alfred 2 has a long-standing bug (which won't be fixed in v2) [#]_
that makes it `one of those places where Python 3 chokes`_ and its automatic
text decoding breaks the world.

Now that Alfred 3 is available and has some significant new features, there is
*no chance* of this version of Alfred-Workflow getting Python 3 support, as
development has effectively stopped in favour of version 2.

When Python 3 support comes, it will be in version 2 or 3 of the library.


.. _full list of new features in Python 2.7: https://docs.python.org/3/whatsnew/2.7.html
.. _include argparse in your workflow: https://pypi.python.org/pypi/argparse
.. _docopt: http://docopt.org/
.. _Powerpack: https://buy.alfredapp.com/
.. _one of those places where Python 3 chokes: http://click.pocoo.org/5/python3/

.. [#] Alfred 2 uses UTF-8 but tells workflows by omission that it's an ASCII
       environment (no locale is set, so Python 3 defaults to the C locale,
       i.e. ASCII, as per the POSIX spec). You *must* specify UTF-8 in the
       environment, e.g. by setting ``PYTHONIOENCODING=UTF-8``, before calling
       ``python3`` otherwise your workflow (any Python 3 code, in fact) will
       die in flames.
