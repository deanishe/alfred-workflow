
.. _text-encoding:

Text encoding/decoding
======================

By default, :class:`Workflow <workflow.workflow.Workflow>` and
:mod:`workflow.web` return command line arguments from Alfred and decoded JSON
data respectively as NFC-normalised Unicode strings.

This is the default for Python. You can change this via the ``input_encoding``
and ``normalization`` keywords to :class:`Workflow <workflow.workflow.Workflow>`
(this will, however, not affect :mod:`workflow.web`, which will *always* return
NFC-encoded Unicode).

If your Workflow works with data from the system (via :mod:`subprocess`,
:func:`os.listdir` etc.), you should almost certainly NFC-normalising those
strings or changing the default normalisation to **NFD**, which is (more or
less) what OS X uses.
:meth:`Workflow.decode() <workflow.workflow.Workflow.decode>` can help with
this.

If you pass a Unicode string to :meth:`~workflow.workflow.Workflow.decode`,
it will just be normalised using the form passed in the ``normalization`` argument
to :meth:`~workflow.workflow.Workflow.decode`
or to :class:`Workflow <workflow.workflow.Workflow>` on instantiation.

If you pass an encoded string, it will be decoded to Unicode with the encoding
passed in the ``encoding`` argument to :meth:`~workflow.workflow.Workflow.decode`
or to :class:`Workflow <workflow.workflow.Workflow>` on instantiation and then
normalised.

Why does normalisation matter?
------------------------------

In Unicode, there isn't a canonical definition of many accented characters.
That is to say, ``ü`` can be represented as ``ü`` or ``u+¨``, depending on the
normalisation form.

Python isn't smart enough to ensure that all Unicode strings are normalised in
the same way.

Therefore, if you're comparing a string containing ``ü`` entered by the user
in Alfred's query box or in the source code (which will be NFC-normalised by
default when using **Alfred-Workflow**) with an ostensibly identical string
that came from OS X's filesystem (which is NFD-normalised), Python won't
recognise them as being the same:

.. code-block:: python
    :linenos:

    >>> from unicodedata import normalize

    >>> data = u'München'  # German for Munich. NFC-normalised as it's Python source code
    >>> print(repr(data))
    u'M\xfcnchen'
    >>> fsdata = normalize('NFD', data)  # The normalisation used by OS X
    u'Mu\u0308nchen'
    >>> data == fsdata
    False

As a result of this misbehaviour of Python (Python 3 is no better in this
regard), it's critical that you ensure that all input is normalised in the same
way.

The bottom line
---------------

If your workflow is based around comparing a user ``query`` to data from the
filesystem, you should call :class:`~workflow.workflow.Workflow` with
``normalization='NFD'``. If your workflow uses data from the Web (via native
Python libraries, including :mod:`workflow.web`), you don't need to do anything
(everything will be NFC-normalised).
