
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
        wf.add_item('Item title', 'Item subtitle')

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
and install your dependencies there. You can call the directory whatever you
want, but in the following explanation, I'll assume you used ``lib``.

To install libraries in your dependencies directory, use:

.. code-block:: bash
    :linenos:

    pip install --target=path/to/my/workflow/lib python-lib-name

The path you pass as the ``--target`` argument should be the path to
the directory under your Workflow's root directory in which you want to install
your libraries. ``python-lib-name`` should be the "pip name" (i.e. the name the
library has on `PyPI <https://pypi.python.org/pypi>`_) of the library you want
to install, e.g. ``requests`` or ``feedparser``.

This name is usually, but not always, the same as the name you use with ``import``.

For example, to install **Alfred-Workflow**, you would run
``pip install Alfred-Workflow`` but use ``import workflow`` to import it.

**An example:** You're in a shell in Terminal.app in the Workflow's root directory
and you're using ``lib`` as the directory for your Python libraries. You want to
install `requests <http://docs.python-requests.org/en/latest/>`_. You would run:

.. code-block:: bash
    :linenos:

    pip install --target=lib requests

This will install the ``requests`` library into the ``lib`` subdirectory of the
current working directory.

Then you instantiate :class:`Workflow <workflow.workflow.Workflow>`
with the ``libraries`` argument:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    def main(wf):
        import requests  # Imported from ./lib

    if __name__ == '__main__':
        wf = Workflow(libraries=['./lib'])
        sys.exit(wf.run(main))

When using this feature you **do not** need to create an ``__init__.py`` file in
the ``lib`` subdirectory. ``Workflow(…, libraries=['./lib'])`` and creating
``./lib/__init__.py`` are effectively equal alternatives.

Instead of using ``Workflow(…, libraries=['./lib'])``, you can add an empty
``__init__.py`` file to your ``lib`` subdirectory and import the libraries
installed therein using:

.. code-block:: python
    :linenos:

    from lib import requests

instead of simply:


.. code-block:: python
    :linenos:

    import requests



.. _persistent-data:

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

The cache directory may be deleted during system maintenance, and is thus only
suitable for temporary data or data that is easily recreated.
:class:`Workflow <workflow.workflow.Workflow>`'s cache methods reflect this,
and make it easy to replace cached data that are too old.
See :ref:`Caching data <caching-data>` for more details.

The data directory is intended for more permanent, user-generated data, or data
that cannot be otherwise easily recreated. See :ref:`Storing data <storing-data>`
for details.

It is easy to specify a custom file format for your stored data
via the ``serializer`` argument if you want your data to be readable by the user
or by other software. See :ref:`Serialization <serialization>` for more details.

There are also simliar methods related to the root directory of your Workflow
(where ``info.plist`` and your code are):

- :attr:`~workflow.workflow.Workflow.workflowdir` — The full path to your Workflow's root directory.
- :meth:`workflowfile(filename) <workflow.workflow.Workflow.workflowfile>` — The full path to ``filename`` under your Workflow's root directory.

These are used internally to implement :ref:`magic arguments <magic-arguments>`, which
may help you with development/debugging.

In addition, :class:`Workflow <workflow.workflow.Workflow>` also provides a
convenient interface for storing persistent settings with
:attr:`Workflow.settings <workflow.workflow.Workflow.settings>`.
See :ref:`Settings <howto-settings>` and :ref:`Keychain access <keychain>` for more
information on storing settings and sensitive data.

.. _caching-data:

Caching data
------------

:class:`Workflow <workflow.workflow.Workflow>` provides a few methods to simplify
caching data that is slow to retrieve or expensive to generate (e.g. downloaded
from a web API). These data are cached in your workflow's cache directory (see
:attr:`~workflow.workflow.Workflow.cachedir`). The main method is
:meth:`Workflow.cached_data() <workflow.workflow.Workflow.cached_data>`, which
takes a name under which the data should be cached, a callable to retrieve
the data if they aren't in the cache (or are too old), and a maximum age in seconds
for the cached data:

.. code-block:: python
    :linenos:

    from workflow import web, Workflow

    def get_data():
        return web.get('https://example.com/api/stuff').json()

    wf = Workflow()
    data = wf.cached_data('stuff', get_data, max_age=600)

To retrieve data only if they are in the cache, call with ``None`` as the
data-retrieval function (which is the default):

.. code-block:: python
    :linenos:

    data = wf.cached_data('stuff', max_age=600)

**Note**: This will return ``None`` if there are no corresponding data in the
cache.

This is useful if you want to update your cache in the background, so it doesn't
impact your Workflow's responsiveness in Alfred. (See
:ref:`the tutorial <background-updates>` for an example of how to run an update
script in the background.)

Passing ``max_age=0`` will return the cached data regardless of age.


.. _storing-data:

Storing data
------------

:class:`Workflow <workflow.workflow.Workflow>` provides two methods to store
and retrieve permanent data:
:meth:`store_data() <workflow.workflow.Workflow.store_data>` and
:meth:`stored_data() <workflow.workflow.Workflow.stored_data>`.

These data are stored in your workflow's data directory
(see :attr:`~workflow.workflow.Workflow.datadir`).

.. code-block:: python
    :linenos:

    from workflow import Workflow

    wf = Workflow()
    wf.store_data('name', data)
    # data will be `None` if there is nothing stored under `name`
    data = wf.stored_data('name')

These methods do not support the data expiry features of the cached data methods,
but you can specify your own serializer for each datastore, making it simple
to store data in, e.g., JSON or YAML format.

You should use these methods (and not the data caching ones) if the data you
are saving should not be deleted as part of system maintenance.

If you want to specify your own file format/serializer, please see
:ref:`Serialization <serialization>` for details.


.. _howto-settings:

Settings
--------

:attr:`Workflow.settings <workflow.workflow.Workflow.settings>` is a subclass
of :class:`dict` that automatically saves its contents to the ``settings.json``
file in your Workflow's data directory when it is changed.

:class:`~workflow.workflow.Settings` can be used just like a normal :class:`dict`
with the caveat that all keys and values must be serializable to JSON.

**Note:** A :class:`~workflow.workflow.Settings` instance can only automatically
recognise when you directly alter the values of its own keys:

.. code-block:: python
    :linenos:

    wf = Workflow()
    wf.settings['key'] = {'key2': 'value'}  # will be automatically saved
    wf.settings['key']['key2'] = 'value2'  # will *not* be automatically saved

If you've altered a data structure stored within your workflow's
:attr:`Workflow.settings <workflow.workflow.Workflow.settings>`, you need to
explicitly call :meth:`Workflow.settings.save() <workflow.workflow.Settings.save>`.

If you need to store arbitrary data, you can use the :ref:`cached data API <caching-data>`.

If you need to store data securely (such as passwords and API keys),
:class:`Workflow <workflow.workflow.Workflow>` also provides :ref:`simple access to
the OS X Keychain <keychain>`.


.. _keychain:

Keychain access
---------------

Methods :meth:`Workflow.save_password(account, password) <workflow.workflow.Workflow.save_password>`,
:meth:`Workflow.get_password(account) <workflow.workflow.Workflow.get_password>`
and :meth:`Workflow.delete_password(account) <workflow.workflow.Workflow.delete_password>`
allow access to the Keychain. They may raise
:class:`~workflow.workflow.Workflow.PasswordNotFound` if no password is set for
the given ``account`` or :class:`~workflow.workflow.Workflow.KeychainError` if
there is a problem accessing the Keychain. Passwords are stored in the user's
default Keychain. By default, the Workflow's Bundle ID will be used as the
service name, but this can be overridden by passing the ``service`` argument
to the above methods.

Example usage:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    wf = Workflow()

    wf.save_password('hotmail-password', 'password1lolz')

    password = wf.get_password('hotmail-password')

    wf.delete_password('hotmail-password')

    # raises PasswordNotFound exception
    password = wf.get_password('hotmail-password')


See :ref:`the relevant part of the tutorial <secure-settings>` for a full example.


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
in the same order, regardless of case. Not only can this lead to unacceptable
performance when working with thousands of results, but it's also very likely
that you'll want to set the standard a little higher.
See :ref:`restricting-results` for info on how to do that.

To use :meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`, pass it
a query, a list of items to filter and sort, and if your list contains items
other than strings, a ``key`` function that generates a string search key for
each item:

.. code-block:: python
    :linenos:

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
    :linenos:

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
at all, or indeed any of the other books. Indeed, they have very low scores:

.. code-block:: python
    :linenos:

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
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`:

.. code-block:: python
    :linenos:

    hits = wf.filter('bot', books, key_for_book, min_score=20)

and/or exclude some of the matching rules:

.. code-block:: python
    :linenos:

    from workflow import Workflow, MATCH_ALL, MATCH_ALLCHARS

    # [...]

    hits = wf.filter('bot', books, key_for_book, match_on=MATCH_ALL ^ MATCH_ALLCHARS)

You can set match rules using bitwise operators, so ``|`` to combine them or
``^`` to remove them from ``MATCH_ALL``:

.. code-block:: python
    :linenos:

    # match only CamelCase and initials
    match_on=MATCH_CAPITALS | MATCH_INITIALS

    # match everything but all-characters-in-item and substring
    match_on=MATCH_ALL ^ MATCH_ALLCHARS ^ MATCH_SUBSTRING

**Note:** ``MATCH_ALLCHARS`` is particularly slow and provides the
worst matches. You should consider excluding it, especially if you're calling
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>` with more than a
few hundred items or expect multi-word queries.

Diacritic folding
-----------------

By default, :meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`
will fold non-ASCII characters to ASCII equivalents (e.g. *é* -> *e*, *ü* -> *u*)
if the ``query`` contains only ASCII characters. This behaviour can be turned
off by passing ``fold_diacritics=False`` to
:meth:`Workflow.filter() <workflow.workflow.Workflow.filter>`.

**Note:** To keep the library small, only a subset of European languages are
supported. The `Unidecode <https://pypi.python.org/pypi/Unidecode>`_ library
should be used for comprehensive support of non-European alphabets.

Users may override a Workflow's default settings via ``workflow:folding…``
:ref:`magic arguments <magic-arguments>`.


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


.. _background-processes:

Background processes
====================

Many workflows provide a convenient interface to applications and/or web services.

For performance reasons, it's common for workflows to cache data locally, but
updating this cache typically takes a few seconds, making your workflow
unresponsive while an update is occurring, which is very un-Alfred-like.

To avoid such delays, **Alfred-Workflow** provides the :mod:`~workflow.background`
module to allow you to easily run scripts in the background.

There are two functions, :func:`~workflow.background.run_in_background` and
:func:`~workflow.background.is_running`, that provide the interface. The
processes started are proper background daemon processes, so you can start
proper servers as easily as simple scripts.

Here's an example of a common usage pattern (updating cached data in the
background). What we're doing is:

1. Check the age of the cached data and run the update script via
    :func:`~workflow.background.run_in_background` if the cached data are too old
    or don't exist.
2. (Optionally) inform the user that data are being updated.
3. Load the cached data regardless of age.
4. Display the cached data (if any).

..  code-block:: python
    :linenos:

    from workflow import Workflow, ICON_INFO
    from workflow.background import run_in_background, is_running

    def main(wf):
       # Is cache over 6 hours old or non-existent?
       if not wf.cached_data_fresh('exchange-rates', 3600):
           run_in_background('update',
                             ['/usr/bin/python',
                              wf.workflowfile('update_exchange_rates.py')])

       # Add a notification if the script is running
       if is_running('update'):
           wf.add_item('Updating exchange rates...', icon=ICON_INFO)

       exchange_rates = wf.cached_data('exchage-rates')

       # Display (possibly stale) cache data
       if exchange_rates:
           for rate in exchange_rates:
               wf.add_item(rate)

       # Send results to Alfred
       wf.send_feedback()

    if __name__ == '__main__':
       wf = Workflow()
       wf.run(main)

For a working example, see :ref:`Part 2 of the Tutorial <background-updates>` or
the `source code <https://github.com/deanishe/alfred-repos/blob/master/src/repos.py>`_
of my `Git Repos <https://github.com/deanishe/alfred-repos>`_ workflow,
which is a bit smarter about showing the user update information.


.. _serialization:

Serialization
=============

By default, both cache and data files (created using the
:ref:`APIs described above <caching-data>`) are cached using :mod:`cPickle`.
This provides a great compromise in terms of speed and the ability to store
arbitrary objects.

When it comes to cache data, it is *strongly recommended* to stick with
the default. :mod:`cPickle` is *very* fast and fully supports standard Python
data structures (``dict``, ``list``, ``tuple``, ``set`` etc.).

If you need the ability to customise caching, you can change the default
cache serialization format to :mod:`pickle` thus:

.. code-block:: python
    :linenos:

    wf = Workflow()
    wf.cache_serializer = 'pickle'

In the case of stored data, you are free to specify either a global default
serializer or one for each individual datastore:

.. code-block:: python
    :linenos:

    wf = Workflow()
    # Use `pickle` as the global default serializer
    wf.data_serializer = 'pickle'

    # Use the JSON serializer only for these data
    wf.store_data('name', data, serializer='json')

This is primarily so you can create files that are human-readable or useable
by non-Python programs.

By default, ``cpickle``, ``pickle`` and ``json`` serializers are available.

You can also register your own custom serializers using the
:class:`~workflow.workflow.SerializerManager` interface.

To register a new serializer, call the ``register`` method of the ``workflow.manager``
object:

.. code-block:: python
    :linenos:

    from workflow import Workflow, manager

    wf = Workflow()
    manager.register('myformat', object_with_load_and_dump_methods)

    wf.store_data('name', data, serializer='myformat')

A serializer *must* conform to this interface (like :mod:`json` and :mod:`pickle`):

.. code-block:: python
    :linenos:

    serializer.load(file_obj)
    serializer.dump(obj, file_obj)


**Note:** The name you use for your serializer will be the file extension
of the stored file.

The :meth:`stored_data() <workflow.workflow.Workflow.stored_data>` method can
automatically determine the serialization of the stored data, provided the
corresponding serializer is registered. If it isn't, a ``ValueError`` will be raised.


Built-in icons
==============

The :mod:`~workflow.workflow` module provides access to a number of default
OS X icons via ``ICON_*`` constants for use when generating Alfred feedback:

.. code-block:: python
    :linenos:

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

:class:`~workflow.workflow.Workflow` supports the following magic arguments:

- ``workflow:openlog`` — Open the Workflow's log file in the default app.
- ``workflow:opencache`` — Open the Workflow's cache directory.
- ``workflow:opendata`` — Open the Workflow's data directory.
- ``workflow:openworkflow`` — Open the Workflow's root directory (where ``info.plist`` is).
- ``workflow:openterm`` — Open a Terminal window in the Workflow's root directory.
- ``workflow:reset`` — Delete the Workflow's settings, cache and saved data.
- ``workflow:delcache`` — Delete the Workflow's cache.
- ``workflow:deldata`` — Delete the Workflow's saved data.
- ``workflow:delsettings`` — Delete the Workflow's settings file (which contains the data stored using :attr:`Workflow.settings <workflow.workflow.Workflow.settings>`).
- ``workflow:foldingon`` — Force diacritic folding in search keys (e.g. convert *ü* to *ue*)
- ``workflow:foldingoff`` — Never fold diacritics in search keys
- ``workflow:foldingdefault`` — Reset diacritic folding to workflow default
- ``workflow:update`` — Self-update workflow if auto update feature is enabled

The three ``workflow:folding…`` settings allow users to override the diacritic
folding set by a workflow's author. This may be useful if the author's choice
does not correspond with a user's usage pattern.

You can turn off magic arguments by passing ``capture_args=False`` to
:class:`~workflow.workflow.Workflow` on instantiation, or call the corresponding
methods of :class:`~workflow.workflow.Workflow` directly, perhaps assigning your
own keywords within your Workflow:

- :meth:`~workflow.workflow.Workflow.open_log`
- :meth:`~workflow.workflow.Workflow.open_cachedir`
- :meth:`~workflow.workflow.Workflow.open_datadir`
- :meth:`~workflow.workflow.Workflow.open_workflowdir`
- :meth:`~workflow.workflow.Workflow.open_terminal`
- :meth:`~workflow.workflow.Workflow.clear_cache`
- :meth:`~workflow.workflow.Workflow.clear_data`
- :meth:`~workflow.workflow.Workflow.clear_settings`
- :meth:`~workflow.workflow.Workflow.reset` (a shortcut to call the three previous ``clear_*`` methods)
