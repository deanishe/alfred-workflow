
.. _text-encoding:

===========================
Encoded strings and Unicode
===========================

.. contents::
   :local:

.. currentmodule:: workflow

This is a brief guide to Unicode and encoded strings aimed at Alfred-Workflow
users (and Python coders in general) who are unfamiliar with them.

Encoding errors are *by far* the most common group of bugs in Python workflows
in the wild (they're so easy for developers to miss).

This guide should give you an idea of what Unicode and encoded strings are,
and why and how you as a workflow developer should deal with them.

.. important::

   String encoding is something Python 2 will let you largely ignore. It will
   happily let you mix strings of different encodings without complaint
   (although the result will most likely be garbage) and if you mix Unicode and
   encoded strings, Python will silently "promote" the encoded string to
   Unicode by decoding it as ASCII. If your workflow only ever uses ASCII, you
   need never worry about Unicode or string encoding.

   But make no mistake: if you distribute your workflow, somebody *will* feed
   your workflow non-ASCII text. Although Alfred is English-only, it's not used
   exclusively by monolingual English speakers. What's more, standard
   English-language characters, like £ or €, are also non-ASCII.

   **If you intend to distribute your workflow, you should make sure it works
   with non-ASCII text.**

   If you don't, I guarantee a text-encoding issue will be one of the first
   bug reports.


TL;DR
=====

Best practice in Python programs is to use Unicode internally and decode
all text input and encode all text output at IO boundaries (i.e. right where
it enters/leaves your program). On macOS, UTF-8 is almost always the right
encoding.

Be sure to decode all input from and encode all output to the system
(in particular via :mod:`subprocess` and when passing a ``{query}`` to a
subsequent workflow action).

If you don't, your workflow *will* break or, at best, not work as intended
when someone feeds it non-ASCII text.

Alfred-Workflow will almost always give you Unicode strings. (The exception is
:class:`web.Response <workflow.web.Response>`, whose
:meth:`~workflow.web.Response.text` method will return an encoded string
if it couldn't determine the encoding.)

Use :meth:`Workflow.decode` to decode input and
``u'My unicode string'.encode('utf-8')`` to encode output, e.g.:

.. code-block:: python
    :linenos:

    #!/usr/bin/python
    # encoding: utf-8

    # Because we want to work with Unicode, it's simpler if we make
    # literal strings in source code Unicode strings by default, so
    # we set `encoding: utf-8` at the very top of the script to tell Python
    # that this source file is UTF-8 and import `unicode_literals` before any
    # code.
    #
    # See Tip further down the page for more info

    from __future__ import unicode_literals, print_function

    import subprocess
    from workflow import Workflow

    wf = Workflow()
    # wf.args decodes and normalizes sys.argv for you
    query = wf.args[0]
    # `subprocess` returns encoded strings (UTF-8 in this case)
    # Note: the arguments are prefixed with `b` because of unicode_literals
    # You should pass encoded strings to `subprocess`. It doesn't much
    # matter in this case, as everything can be encoded to ASCII, but if you're
    # passing in, say, a user-supplied query, be sure to encode it to UTF-8
    output = subprocess.check_output([b'mdfind', b'-onlyin',
                                      os.getenv('HOME'),
                                      b'kind:folder date:today'])
    # Convert to Unicode and NFC-normalize
    output = wf.decode(output)
    # Split the output into individual filepaths
    paths = [s.strip() for s in output.split('\n') if s.strip()]
    # Filter paths by query
    paths = wf.filter(query, paths,
                      # We just want to filter on filenames, not the whole path
                      key=lambda s: os.path.basename(s),
                      min_score=30)

    if paths:
       # For demonstration purposes, pass the first result as `{query}`
       # to the next workflow Action.
       print(paths[0].encode('utf-8'))


String types
============

In Python, there are two different kind of strings: Unicode and encoded strings.

Unicode strings only exist within running programs (Unicode is a concept rather
than a concrete implementation), while encoded strings are binary data that are
encoded according to some scheme that maps characters to a specific binary
representation (e.g. UTF-8 or ASCII).

In Python, these have the types ``unicode`` and ``str`` respectively.

As noted, Unicode strings only exist within a running program. Any text stored
on disk, passed into or out of a program or transmitted over a network *must*
be encoded. On macOS, almost all text (e.g. filenames, most text output from
programs) is encoded with UTF-8.

In order for your program to work properly, it's important to ensure that all
text is of the same type/encoding:

.. code-block:: python

    >>> u = u'Fahrvergnügen'  # This is a Unicode string
    >>> enc1 = u.encode('utf-8')  # macOS default encoding
    >>> enc2 = u.encode('latin-1')  # Older standard German encoding
    >>> enc1 == enc2
    False
    >>> u == enc1
    UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
    False
    >>> unicode(enc1, 'utf-8') == unicode(enc2, 'latin-1')
    True

The correct way to do this in Python is to decode all text input to Unicode
as soon as it enters your program. In particular, this means:

- Command-line arguments (via :data:`sys.argv`)
- Environmental variables (via :data:`os.environ`)
- The contents of text files (via :func:`open`)
- Data retrieved from the web (via :func:`urllib.urlopen`)
- The output of subprocesses (via :func:`subprocess.check_output` or
  :class:`subprocess.Popen` etc.)
- Filepaths (via :func:`os.listdir` etc.). Sometimes. Basically, if you
  pass a Unicode string to a filesystem function, you'll get Unicode back. If
  you pass an encoded string, you'll get an encoded (UTF-8) string back.

Alfred-Workflow uses Unicode throughout, and any command-line arguments
(:attr:`Workflow.args`), environmental variables (:attr:`Workflow.alfred_env`),
or data from the web (e.g. :func:`web.Response.text <workflow.web.Response.text>`)
will be decoded to Unicode for you.

As a result of this, it's important that you also decode any text your workflow
pulls in from other sources. When you combine Unicode and encoded strings in
Python 2, Python will "promote" the encoded string to Unicode by attempting
to decode it as ASCII. In many cases this will work, but if the encoded string
contains characters that aren't in ASCII (e.g. £ or ü or —), your workflow
will die in flames.

.. tip::

    Always test your workflow with non-ASCII input to flush out any accidental
    mixing of Unicode and encoded strings.


:class:`Workflow` provides the convenience method :meth:`Workflow.decode()`
for working with Unicode and encoded strings. You can pass it Unicode or encoded
strings and it will return normalized Unicode. You can specify the encoding
and normalization form with the ``input_encoding`` and ``normalization``
arguments to :class:`Workflow` or with the ``encoding`` and
``normalization`` arguments to :meth:`Workflow.decode()`. Generally,
you shouldn't need to change the default encoding of UTF-8, which is what
macOS uses, but you may need to alter the normalization depending on where
your workflow gets its data from.


.. tip::

    To save yourself from having to prefix every string in your source code
    with ``u`` to mark it as a Unicode string, add
    ``from __future__ import unicode_literals`` at the top of your Python
    scripts. This makes all unprefixed strings Unicode by default (use ``b''``
    to create an encoded string). Add ``# encoding: utf-8`` to the top of your
    source files to tell Python that the source code is UTF-8.

    Encoded strings by default:

    .. code-block:: python

        # encoding: utf-8

        ustr = u'This is a Unicode string'
        bstr = 'This is a UTF-8 encoded string'

    Unicode by default:

    .. code-block:: python

        # encoding: utf-8
        from __future__ import unicode_literals

        ustr = 'This is a Unicode string'
        bstr = b'This is a UTF-8 encoded string'


Normalization
=============

Unicode provides multiple ways to represent the same character. Normalization
is the process of ensuring that all instances of a given Unicode character are
represented in the same way.


TL;DR
-----

Normalize *all* input.

Nitty-Gritty
------------

If your workflow is based around comparing a user ``query`` to data from the
system (filepaths, output of command-line programs), you should instantiate
:class:`Workflow` with the ``normalization='NFD'`` argument.

If your workflow uses data from the Web (via native Python libraries, including
:mod:`~workflow.web`), you probably don't need to do anything
(everything will be NFC-normalized).

If you're mixing both kinds of data, the simplest solution is probably to run
all data from the system through :meth:`Workflow.decode()` to ensure it is
normalized in the same way as data from the Web.


Why does normalization matter?
------------------------------

In Unicode, accented characters can be represented in different ways, e.g. ``ü``
can be represented as ``ü`` or as ``u+¨``. Unfortunately, Python doesn't ensure
that all Unicode strings are normalized to use the same representations when
comparing them.

Therefore, if you're comparing a string containing ``ü`` that came from a
JSON file (which will typically be NFC-normalized) with an ostensibly identical
string that came from macOS's filesystem (which is NFD-normalized), Python won't
recognise them as being the same:

.. code-block:: python

    >>> from unicodedata import normalize
    >>> from glob import glob
    >>> name = u'München.txt'  # German for 'Munich'. NFC-normalized, as it's Python source code
    >>> print(repr(name))
    u'M\xfcnchen.txt'
    >>> open(name, 'w').write('')  # Create an empty text file called `München.txt`

    >>> for filename in glob(u'*.txt'):
    ...     if filename == name:
    ...         print(u'Match : {0} ({0!r}) == {1} ({1!r})'.format(filename, name))
    ...     else:
    ...         print(u'No match : {0} ({0!r}) != {1} ({1!r})'.format(filename, name))
    ...
    # The filename has been NFD-normalized by the filesystem
    No match : München.txt (u'Mu\u0308nchen.txt') != München.txt (u'M\xfcnchen.txt')
    >>> for filename in glob(u'*.txt'):
    ...     filename = normalize('NFC', filename)  # Ensure the same normalization
    ...     if filename == name:
    ...         print(u'Match : {0} ({0!r}) == {1} ({1!r})'.format(filename, name))
    ...     else:
    ...         print(u'No match : {0} ({0!r}) != {1} ({1!r})'.format(filename, name))
    ...
    Match : München.txt (u'M\xfcnchen.txt') == München.txt (u'M\xfcnchen.txt')


As a result of this Unicode quirk, it's important to ensure that all input is
normalized in the same way or, for example, a user-provided query
(which may be NFC- or NFD-normalized) may not match JSON data pulled from an API
(which is probably NFC-normalized) even though they are ostensibly the same.


Normalization with Alfred-Workflow
----------------------------------

.. note::

  This behaviour of Alfred-Workflow is not 100% correct. There are some strings
  (notably in Asian alphabets) that cannot be represented in all normalization
  forms, particularly NFC, which Alfred-Workflow uses by default. However, I
  decided to NFC-normalize all text you will get from Alfred-Workflow by
  default, as this will work as expected in 99+% of cases, and insulate
  Alfred-Workflow users from much of the pain of text encoding.

By default, :class:`Workflow` and :mod:`~workflow.web` return command
line arguments from Alfred and text/decoded JSON data respectively as
NFC-normalized Unicode strings.

This is the default for Python. You can change this via the ``normalization``
keyword to :class:`Workflow` (this will, however, not affect
:mod:`~workflow.web`, which *always* returns NFC-encoded Unicode
strings).

If your workflow works with data from the system (via :mod:`subprocess`,
:func:`os.listdir` etc.), you should probably be NFC-normalizing those
strings or changing the default normalization to ``NFD``, which is (more or
less) what macOS and Alfred use. :meth:`Workflow.decode()` can help with this.

If you pass a Unicode string to :meth:`Workflow.decode`, it will be normalized
using the form passed in the ``normalization`` argument
to :meth:`Workflow.decode` or to :class:`Workflow` on instantiation.

If you pass an encoded string, it will be decoded to Unicode with the encoding
passed in the ``encoding`` argument to :meth:`Workflow.decode` or the
``input_encoding`` argument to :class:`Workflow` on instantiation and then
normalized as above.


Other Gotchas
=============

Well, only one big gotcha: locale.

.. note:: This is only really important in Alfred 2.


POSIX software, like your shell, Python, Ruby and other command-line
tools, use the encoding specified in your environment.

Your shell probably has a sensible encoding set via ``$LANG`` or another
environment variable:

.. code-block:: bash

  $ echo $LANG
  en_GB.UTF-8

This tells software that wants to decode input that it should use UTF-8,
which is the encoding that Alfred uses.

Alfred 3 runs your scripts in a UTF-8 environment, but Alfred 2 runs them in
an empty environment. This tells Python (and other POSIX software) by omission
that encoding is ASCII.

Although this won't affect Python 2's auto-promotion of encoded strings
(``str`` objects) to Unicode (it always uses ASCII), it *does*
affect the printing of Unicode strings, so using :func:`print` may work
perfectly in your shell where the environmental encoding is UTF-8 but not in
Alfred 2, where encoding is ASCII by default.

Be sure to print Unicode strings with
``print(my_unicode_string.encode('utf-8'))`` (e.g. when passing an argument to
an **Open URL** Action or **Post Notification** Output)!


Further information
===================

If you're unfamiliar with using Unicode in Python, have a look at the official
Python `Unicode HOWTO`_.

.. _Unicode HOWTO: https://docs.python.org/2/howto/unicode.html

