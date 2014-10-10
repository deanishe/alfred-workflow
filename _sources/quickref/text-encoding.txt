
.. _text-encoding:

A note on text encoding/decoding
================================

By default, :class:`Workflow <workflow.workflow.Workflow>` (and :mod:`workflow.web`)
return command line arguments from Alfred as NFC-normalised Unicode strings.
This is the default for Python. You can change this via the ``input_encoding``
and ``normalization`` keywords to :class:`Workflow <workflow.workflow.Workflow>`
(this will not affect :mod:`workflow.web`).

If your Workflow works with data from the system (via :mod:`subprocess`,
:func:`os.listdir` etc.), you should consider also NFC-normalising those strings
or changing the default normalisation to **NFD**, which is (more or less) what
OS X uses. :meth:`Workflow.decode() <workflow.workflow.Workflow.decode>` can
help with this.

If you pass a Unicode string to :meth:`~workflow.workflow.Workflow.decode`,
it will just be normalised using the form passed in the ``normalization`` argument
to :meth:`~workflow.workflow.Workflow.decode`
or to :class:`Workflow <workflow.workflow.Workflow>` on instantiation.

If you pass an encoded string, it will be decoded to Unicode with the encoding
passed in the ``encoding`` argument to :meth:`~workflow.workflow.Workflow.decode`
or to :class:`Workflow <workflow.workflow.Workflow>` on instantiation and then
normalised.
