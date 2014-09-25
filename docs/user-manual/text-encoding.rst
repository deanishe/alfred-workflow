
.. _text-encoding:

Encoded strings and Unicode
===========================

Alfred-Workflow uses Unicode throughout, which is something you should aim to
do when working with text in Python. If your code naïvely mixes Unicode and
encoded strings, it will fail if an encoded string contains non-ASCII
characters.

Python 3 has much improved this situation, but is currently not installed on
OS X by default, so isn't supported by Alfred or Alfred-Workflow.

.. tip::

    Always test your workflow with non-ASCII input to flush out any accidental
    mixing of Unicode and encoded strings.


:class:`Workflow <workflow.workflow.Workflow>` provides the convenience method
:meth:`Workflow.decode() <workflow.workflow.Workflow.decode>` for working with
Unicode and encoded strings. You can pass it Unicode or encoded strings and it
will return normalised Unicode. You can specify the encoding and normalisation
form with the ``input_encoding`` and ``normalization`` arguments to
:class:`Workflow <workflow.workflow.Workflow>` or with the ``encoding`` and
``normalization`` arguments to
:meth:`Workflow.decode() <workflow.workflow.Workflow.decode>`. Generally,
you shouldn't need to change the default encoding of UTF-8, which is what
OS X uses, but you may need to alter the normalisation depending on where
your workflow gets its data from.


.. tip::

    To save yourself from having to prefix every string in your source code
    with ``u``, add ``from __future__ import unicode_literals`` at the top of
    your Python scripts. This makes all unprefixed strings Unicode by default
    (use ``b''`` to create an encoded string):

    .. code-block:: python
        :linenos:

        # encoding: utf-8
        from __future__ import unicode_literals

        ustr = 'This is a Unicode string'
        bstr = b'This is an encoded string'


Normalisation
-------------

Normalisation is the process of ensuring that all instances of a given
Unicode character are represented in the same way.

In Unicode, an accented character like ``ü`` can be represented as ``ü`` or as
``u+¨``. By normalising Unicode strings, you ensure that all instances of ``ü``
are represented in the same way.

The bottom line
^^^^^^^^^^^^^^^

If your workflow is based around comparing a user ``query`` to data from the
filesystem, you should call :class:`~workflow.workflow.Workflow` with
``normalization='NFD'``. If your workflow uses data from the Web (via native
Python libraries, including :mod:`workflow.web`), you probably don't need to
do anything (everything will be NFC-normalised). If you're mixing both kinds
of data, the simplest solution is probably to run all data from the filesystem
through :meth:`Workflow.decode() <workflow.workflow.Workflow.decode>` to
ensure it is normalised in the same way as data from the Web.

Why does normalisation matter?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As noted above, in Unicode a character like ``ü`` can be represented as ``ü``
or ``u+¨``.

Python isn't smart enough to ensure that all Unicode strings are normalised to
use the same representations when comparing them.

Therefore, if you're comparing a string containing ``ü`` entered by the user
in Alfred's query box or in the source code (which will be NFC-normalised by
default when using Alfred-Workflow) with an ostensibly identical string
that came from OS X's filesystem (which is NFD-normalised), Python won't
recognise them as being the same:

.. code-block:: python
    :linenos:

    >>> from unicodedata import normalize

    >>> data = u'München'  # German for Munich. NFC-normalised as it's Python source code
    >>> print(repr(data))
    u'M\xfcnchen'
    >>> fsdata = normalize('NFD', data)  # The normalisation used by OS X
    >>> print(repr(fsdata))
    u'Mu\u0308nchen'
    >>> print(data)
    München
    >>> print(fsdata)
    München
    >>> data == fsdata
    False

As a result of this Python quirk (Python 3 is alas no better in this regard),
it's important to ensure that all input is normalised in the same way or, for
example, a user-provided query may not match a filename that it should.


Normalisation with Alfred-Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, :class:`Workflow <workflow.workflow.Workflow>` and
:mod:`workflow.web` return command line arguments from Alfred and text/decoded
JSON data respectively as NFC-normalised Unicode strings.

This is the default for Python. You can change this via the ``input_encoding``
and ``normalization`` keywords to :class:`Workflow <workflow.workflow.Workflow>`
(this will, however, not affect :mod:`workflow.web`, which *always* returns
NFC-encoded Unicode strings).

If your workflow works with data from the system (via :mod:`subprocess`,
:func:`os.listdir` etc.), you should almost certainly be NFC-normalising those
strings or changing the default normalisation to **NFD**, which is (more or
less) what OS X uses.
:meth:`Workflow.decode() <workflow.workflow.Workflow.decode>` can help with
this.

If you pass a Unicode string to :meth:`~workflow.workflow.Workflow.decode`,
it will just be normalised using the form passed in the ``normalization``
argument to :meth:`~workflow.workflow.Workflow.decode`
or to :class:`Workflow <workflow.workflow.Workflow>` on instantiation.

If you pass an encoded string, it will be decoded to Unicode with the encoding
passed in the ``encoding`` argument to :meth:`~workflow.workflow.Workflow.decode`
or the ``input_encoding`` argument to
:class:`Workflow <workflow.workflow.Workflow>` on instantiation and then
normalised as above.


Further information
-------------------

If you're unfamiliar with using Unicode in Python, have a look at the official
Python `Unicode HOWTO`_.

.. _Unicode HOWTO: https://docs.python.org/2/howto/unicode.html

