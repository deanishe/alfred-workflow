
.. _osx-versions:

=======================
Supported OS X versions
=======================

Alfred 2 supports every version of OS X from 10.6 (Snow Leopard).
Alfred-Workflow also supports the same versions, but there are a couple of
things you have to watch out for because 10.6 has Python 2.6, while later
versions have Python 2.7. As a result, if you want to maximise the
compatibility of your workflow, you need to avoid using 2.7-only features in
your code.

Here is the `full list of new features in Python 2.7`_, but the
most important things if you want your workflow to run on Snow
Leopard are:

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

.. _full list of new features in Python 2.7: https://docs.python.org/3/whatsnew/2.7.html
.. _include argparse in your workflow: https://pypi.python.org/pypi/argparse
.. _docopt: http://docopt.org/
