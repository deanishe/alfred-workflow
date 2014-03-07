
=====
Howto
=====

This document serves as a quick reference on using the features of
**Alfred-Python**.

If you're new to writing Workflows or coding in general, start with the
:ref:`Tutorial <tutorial>`.



Workflow setup and skeleton
===========================

**Alfred-Python** is aimed particularly at authors of so-called
**Script Filters**. These are activated by a keyword in Alfred, receive
user input and return results to Alfred.

To write a Script Filter with **Alfred-Workflow**, make sure your Script Filter
is set to use ``/bin/bash`` as the **Language**, and select the
following (and only the following) **Escaping** options:

- Backquotes
- Double Quotes
- Dollars
- Backslashes

The **Script** field should contain the following::

    python yourscript.py "{query}"


where ``yourscript.py`` is the name of your script.

Your workflow should start out like this. This enables :class:`Workflow`
to capture any errors thrown by your scripts:

.. code-block:: python
   :linenos:

    #!/usr/bin/python
    # encoding: utf-8

    import sys

    from workflow import Workflow

    log = None


    def main(wf):
        # The Workflow instance will be passed to the function
        # you call from `Workflow.run`

        # Your imports here if you want to catch import errors
        import somemodule
        import anothermodule

        # Get args from Workflow as normalised Unicode
        args = wf.args

        # Do stuff here ...

        # Add an item to Alfred feedback
        wf.add_item(u'Item title', u'Item subtitle')

        # Send output to Alfred
        wf.send_feedback()


    if __name__ == '__main__':
        wf = Workflow()
        # Assign Workflow logger to a global variable, so all module
        # functions can access it without having to pass the Workflow
        # instance around
        log = wf.logger
        sys.exit(wf.run(main))


Including 3rd party libraries
=============================

It's a Very Bad Idea ™ to install (or ask users to install) 3rd-party libraries
in the OS X system Python. **Alfred-Workflow** makes it easy to include them in
your Workflow.

Simply create a ``lib`` subdirectory under your Workflow's root directory
(or call it whatever you want), install your dependencies there with

.. code-block:: bash

    pip install --target=my-workflow-root-dir/lib my-workflows-dependency

and instantiate :class:`Workflow <workflow.workflow.Workflow>`
with the ``libraries`` argument::

    from workflow import Workflow

    def main(wf):
        import module_from_lib_subdirectory_here

    if __name__ == '__main__':
        wf = Workflow(libraries=['./lib'])
        sys.exit(wf.run(main))


Persistent data
===============

Alfred provides special data and cache directories for each Workflow (in
``~/Library/Application Support`` and ``~/Library/Caches`` respectively).
:class:`Workflow <workflow.workflow.Workflow>` provides the following
attributes/methods to make it easier to access these directories:

- :attr:`~workflow.workflow.Workflow.datadir` — The full path to your Workflow's data directory.
- :attr:`~workflow.workflow.Workflow.cachedir` — The full path to your Workflow's cache directory.
- :meth:`datafile(filename) <workflow.workflow.Workflow.datafile>` — The full path to ``filename`` under the data directory.
- :meth:`cachefile(filename) <workflow.workflow.Workflow.cachefile>` — The full path to ``filename`` under the cache directory.

There are also corresponding features related to the root directory of your Workflow
(where ``info.plist`` and your code are):

- :attr:`~workflow.workflow.Workflow.workflowdir` — The full path to your Workflow's root directory.
- :meth:`datafile(filename) <workflow.workflow.Workflow.workflowfile>` — The full path to ``filename`` under your Workflow's root directory.

These are used internally to implement `magic arguments <magic-arguments>`, which
may help you with development/debugging.

In addition, :class:`Workflow <workflow.workflow.Workflow>` also provides a
convenient interface for storing persistent settings with
:attr:`Workflow.settings <workflow.workflow.Workflow.settings>`.


Settings
--------

:attr:`Workflow.settings <workflow.workflow.Workflow.settings>` is a subclass
of :class:`dict` that automatically saves its contents to the ``settings.json``
file in your Workflow's data directory when it is changed.

:class:`~workflow.workflow.Settings` can be used just like a normal :class:`dict`
with the caveat that all keys and values must be serialisable to JSON.

If you need to store arbitrary data, you can use the :ref:`cached data API <caching-data>`.

If you need to store data securely (such as passwords and API keys),
:class:`Workflow <workflow.workflow.Workflow>` also provides simple access to
the OS X Keychain.


Keychain access
---------------

Methods :meth:`Workflow.save_password(account, password) <workflow.workflow.Workflow.save_password>`,
:meth:`Workflow.get_password(account) <workflow.workflow.Workflow.get_password>`
and :meth:`Workflow.delete_password(account) <workflow.workflow.Workflow.delete_password>`
allow access to the Keychain. They may raise
:class:`PasswordNotFound <workflow.workflow.Workflow.PasswordNotFound>` if
no password is set for the given ``account`` or
:class:`KeychainError <workflow.workflow.Workflow.KeychainError>` if there is
a problem accessing the Keychain. Passwords are stored in the user's default
Keychain. By default, the Workflow's Bundle ID will be used as the service name,
but this can be overridden by setting the ``service`` argument to the above
methods.

Example usage::

    from workflow import Workflow

    wf = Workflow()

    wf.save_password('hotmail-password', 'password1lolz')

    password = wf.get_password('hotmail-password')

    wf.delete_password('hotmail-password')

    # raises PasswordNotFound exception
    password = wf.get_password('hotmail-password')


See :ref:`the relevant part of the tutorial <secure-settings>` for a full example.



.. _caching-data:

Caching data
------------

:class:`Workflow <workflow.workflow.Workflow>` provides a few methods to simplify
caching data that is slow to retrieve or expensive to generate. The main method
is :meth:`Workflow.cached_data() <workflow.workflow.Workflow.cached_data>`, which
takes a name under which the data should be cached, a callable to retrieve
the data if they aren't in the cache (or are too old), and a maximum age in seconds
for the cached data::

    from workflow import web, Workflow

    def get_data():
        return web.get('https://example.com/api/stuff').json()

    wf = Workflow()
    data = wf.cached_data('stuff', get_data, max_age=600)

To only retrieve data if they are in the cache, call with ``None`` as the
data-retrieval function (which is the default)::

    data = wf.cached_data('stuff', max_age=600)

**Note**: This will return ``None`` if there are no corresponding data in the
cache.

This is useful if you want to update your cache in the background, so it doesn't
impact your Workflow's responsiveness in Alfred. (See
:ref:`the tutorial <background-updates>` for an example of how to run an update
script in the background.)

Passing ``max_age=0`` will return the cached data regardless of age.



.. _filtering:

Searching/filtering data
========================

:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>` provides an
Alfred-like search algorithm for filtering your Workflow's data. By default,
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>` will try to match
your search query via CamelCase, substring, initials and all characters, applying
different weightings to the various kind of matches (see
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>` for a detailed
description of the algorithm and match flags).

**Note:** By default, :meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`
will match and return anything that contains all the characters in ``query``
in the same order, regardless of case. It's very likely that you'll want to set
the standard a little higher. See :ref:`restricting-results` for info on how
to do that.

To use :meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`, pass it
a query, a list of items to filter and sort, and if your list contains items
other than strings, a ``key`` function that generates a string search key for
each item::

    from workflow import Workflow

    names = ['Bob Smith', 'Carrie Jones', 'Harry Johnson', 'Sam Butterkeks']

    wf = Workflow()

    hits = wf.filter('bs', names)

Which returns::

    ['Bob Smith', 'Sam Butterkeks']

(``bs`` are Bob Smith's initials and ``Butterkeks`` contains both letters in that order.)


If your data are not strings:

.. code-block:: python
   :emphasize-lines: 11-12,16

    from workflow import Workflow

    books = [
        {'title': 'A damn fine afternoon', 'author': 'Bob Smith'},
        {'title': 'My splendid adventure', 'author': 'Carrie Jones'},
        {'title': 'Bollards and other street treasures', 'author': 'Harry Johnson'},
        {'title': 'The horrors of Tuesdays', 'author': 'Sam Butterkeks'}
    ]


    def key_for_book(book):
        return '{} {}'.format(book['title'], book['author'])

    wf = Workflow()

    hits = wf.filter('bot', books, key_for_book)

Which returns::

    [{'author': 'Harry Johnson', 'title': 'Bollards and other street treasures'},
     {'author': 'Bob Smith', 'title': 'A damn fine afternoon'}]


.. _restricting-results:

Restricting results
-------------------

Chances are, you would not want ``bot`` to match ``Bob Smith A damn fine afternoon``
at all, or indeed any of the other books. Indeed, they have very low scores::

    hits = wf.filter('bot', books, key_for_book, include_score=True)

produces::

    [({'author': 'Bob Smith', 'title': 'A damn fine afternoon'},
      11.11111111111111,
      64),
     ({'author': 'Harry Johnson', 'title': 'Bollards and other street treasures'},
      3.3333333333333335,
      64),
     ({'author': 'Sam Butterkeks', 'title': 'The horrors of Tuesdays'}, 3.125, 64)]

(``64`` is the rule that matched, ``MATCH_ALLCHARS``, which matches
if all the characters in ``query`` appear in order in the search key, regardless
of case).

If we filter ``{'author': 'Brienne of Tarth', 'title': 'How to beat up men'}`` and
``{'author': 'Zoltar', 'title': 'Battle of the Planets'}``, which we probably
would want to match ``bot``, we get::

    [({'author': 'Zoltar', 'title': 'Battle of the Planets'}, 98.0, 8),
     ({'author': 'Brienne of Tarth', 'title': 'How to beat up men'}, 90.0, 16)]

(The ranking would be reversed if ``key_for_book()`` returned ``author title``
instead of ``title author``.)

So in all likelihood, you'll want to pass a ``min_score`` argument to
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`::

    hits = wf.filter('bot', books, key_for_book, min_score=20)

and/or exclude some of the matching rules::

    from workflow import Workflow, MATCH_ALL, MATCH_ALLCHARS

    # [...]

    hits = wf.filter('bot', books, key_for_book, match_on=MATCH_ALL ^ MATCH_ALLCHARS)

You can set match rules using bitwise operators, so ``|`` to combine them or
``^`` to remove them from ``MATCH_ALL``::

    # match only CamelCase and initials
    match_on=MATCH_CAPITALS | MATCH_INITIALS

    # match everything but all-characters-in-item and substring
    match_on=MATCH_ALL ^ MATCH_ALLCHARS ^ MATCH_SUBSTRING

**Note:** ``MATCH_ALLCHARS`` is particularly slow and provides the
worst matches. You should consider excluding it, especially if you're calling
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>` with > 5000 items.

Text encoding/decoding
======================

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



Built-in icons
==============

The :mod:`~workflow.workflow` module provides access to a number of default
OS X icons via ``ICON_*`` constants for use when generating Alfred feedback::

    from workflow import Workflow, ICON_INFO

    wf = Workflow()
    wf.add_item('For your information', icon=ICON_INFO)
    wf.send_feedback()


.. _icon-list:

List of icons
-------------

These are all the icons accessible in :mod:`~workflow.workflow`. They (and more) can
be found in ``/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/``.

+-------------------+-------------------------------------+
| Name              | Preview                             |
+===================+=====================================+
|``ICON_ACCOUNT``   |.. image:: _static/ICON_ACCOUNT.png  |
+-------------------+-------------------------------------+
|``ICON_BURN``      |.. image:: _static/ICON_BURN.png     |
+-------------------+-------------------------------------+
|``ICON_COLOR``     |.. image:: _static/ICON_COLOR.png    |
+-------------------+-------------------------------------+
|``ICON_COLOUR``    |.. image:: _static/ICON_COLOUR.png   |
+-------------------+-------------------------------------+
|``ICON_ERROR``     |.. image:: _static/ICON_ERROR.png    |
+-------------------+-------------------------------------+
|``ICON_FAVORITE``  |.. image:: _static/ICON_FAVORITE.png |
+-------------------+-------------------------------------+
|``ICON_FAVOURITE`` |.. image:: _static/ICON_FAVOURITE.png|
+-------------------+-------------------------------------+
|``ICON_GROUP``     |.. image:: _static/ICON_GROUP.png    |
+-------------------+-------------------------------------+
|``ICON_HELP``      |.. image:: _static/ICON_HELP.png     |
+-------------------+-------------------------------------+
|``ICON_INFO``      |.. image:: _static/ICON_INFO.png     |
+-------------------+-------------------------------------+
|``ICON_MUSIC``     |.. image:: _static/ICON_MUSIC.png    |
+-------------------+-------------------------------------+
|``ICON_NETWORK``   |.. image:: _static/ICON_NETWORK.png  |
+-------------------+-------------------------------------+
|``ICON_NOTE``      |.. image:: _static/ICON_NOTE.png     |
+-------------------+-------------------------------------+
|``ICON_SETTINGS``  |.. image:: _static/ICON_SETTINGS.png |
+-------------------+-------------------------------------+
|``ICON_SYNC``      |.. image:: _static/ICON_SYNC.png     |
+-------------------+-------------------------------------+
|``ICON_TRASH``     |.. image:: _static/ICON_TRASH.png    |
+-------------------+-------------------------------------+
|``ICON_USER``      |.. image:: _static/ICON_USER.png     |
+-------------------+-------------------------------------+
|``ICON_WARNING``   |.. image:: _static/ICON_WARNING.png  |
+-------------------+-------------------------------------+
|``ICON_WEB``       |.. image:: _static/ICON_WEB.png      |
+-------------------+-------------------------------------+

.. _magic-arguments:

"Magic" arguments
=================

If your Script Filter (or script) accepts a query (or command line arguments),
you can pass it so-called magic arguments that instruct
:class:`~workflow.workflow.Workflow` to perform certain actions, such as
opening the log file or clearing the cache/settings.

These can be a big help while developing and debugging and especially when
debugging problems your Workflow's users may be having.

The :meth:`Workflow.run() <~workflow.workflow.Workflow.run>` method
(which you should "wrap" your Workflow's entry functions in) will catch any
raised exceptions, log them and display them in Alfred. You can call your
Workflow with ``workflow:openlog`` as an Alfred query/command line argument
and :class:`~workflow.workflow.Workflow` will open the Workflow's log file
in the default app (usually **Console.app**).

This makes it easy for you to get at the log file and data and cache directories
(hidden away in ``~/Library``), and for your users to send you their logs
for debugging.

**Note:** Magic arguments will only work with scripts that accept arguments *and*
use the :attr:`~workflow.workflow.Workflow.args` property (where magic arguments
are parsed).

:class:`~workflow.workflow.Workflow` supports the following magic args:

- ``workflow:openlog`` — Open the Workflow's log file in the default app.
- ``workflow:opencache`` — Open the Workflow's cache directory.
- ``workflow:opendata`` — Open the Workflow's data directory.
- ``workflow:openworkflow`` — Open the Workflow's root directory (where ``info.plist`` is).
- ``workflow:delcache`` — Delete any data cached by the Workflow.
- ``workflow:delsettings`` — Delete the Workflow's settings file (which contains the data stored using :attr:`Workflow.settings <workflow.workflow.Workflow.settings>`).

You can turn off magic arguments by passing ``capture_args=False`` to
:class:`~workflow.workflow.Workflow` on instantiation, or call the corresponding
:meth:`~workflow.workflow.Workflow.open_log`, :meth:`~workflow.workflow.Workflow.clear_cache`
and :meth:`~workflow.workflow.Workflow.clear_settings` methods directly, perhaps
assigning them to your own Keywords.
