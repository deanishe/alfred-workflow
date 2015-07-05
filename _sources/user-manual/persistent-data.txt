
.. _manual-persistent-data:

===============
Persistent data
===============

.. note::

    If you are writing your own files without using the
    :class:`Workflow <workflow.workflow.Workflow>` APIs, please see
    :ref:`script-behaviour`.

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
See :ref:`Caching data <caching-data>` for details of the data caching API.

The data directory is intended for more permanent, user-generated data, or data
that cannot be otherwise easily recreated. See :ref:`Storing data <storing-data>`
for details of the data storage API.

It is easy to specify a custom file format for your stored data
via the ``serializer`` argument if you want your data to be readable by the user
or by other software. See :ref:`manual-serialization` for more details.

.. tip::

    There are also simliar methods related to the root directory of your
    Workflow (where ``info.plist`` and your code are):

    - :attr:`~workflow.workflow.Workflow.workflowdir` — The full path to your
      Workflow's root directory.
    - :meth:`workflowfile(filename) <workflow.workflow.Workflow.workflowfile>`
      — The full path to ``filename`` under your Workflow's root directory.

    These are used internally to implement :ref:`magic-arguments`, which
    provide assistance with debugging, updating and managing your workflow.

In addition, :class:`Workflow <workflow.workflow.Workflow>` also provides a
convenient interface for storing persistent settings with
:attr:`Workflow.settings <workflow.workflow.Workflow.settings>`.
See :ref:`Settings <manual-settings>` and :ref:`Keychain access <keychain>` for more
information on storing settings and sensitive data.

.. _caching-data:

Caching data
============

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

    data = wf.cached_data('stuff', max_age=600)

.. note:: This will return ``None`` if there are no corresponding data in the cache.

This is useful if you want to update your cache in the background, so it doesn't
impact your Workflow's responsiveness in Alfred. (See
:ref:`the tutorial <background-updates>` for an example of how to run an update
script in the background.)

.. tip:: Passing ``max_age=0`` will return the cached data regardless of age.


.. _clearing-cache:

Clearing cached data
--------------------

There is a convenience method for clearing a workflow's cache directory.

:meth:`~workflow.workflow.Workflow.clear_cache` will by default delete all
the files contained in :attr:`~workflow.workflow.Workflow.cachedir`. This is
the method called if you use the ``workflow:delcache`` or ``workflow:reset``
:ref:`magic arguments <magic-arguments>`.

You can selectively delete files from the cache by passing the optional
``filter_func`` argument to :meth:`~workflow.workflow.Workflow.clear_cache`.
This callable will be called with the filename (not path) of each file in the
workflow's cache directory.

If ``filter_func`` returns ``True``, the file will be deleted, otherwise it
will be left in the cache. For example, to delete all ``.zip`` files in the
cache, use:

.. code-block:: python
    :linenos:

    def myfilter(filename):
        return filename.endswith('.zip')

    wf.clear_cache(myfilter)

or more simply:

.. code-block:: python
    :linenos:

    wf.clear_cache(lambda f: f.endswith('.zip'))


.. _storing-data:

Storing data
============

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
:ref:`manual-serialization` for details.


.. _clearing-data:

Clearing stored data
--------------------

As with cached data, there is a convenience method for deleting all the files
stored in your workflow's :attr:`~workflow.workflow.Workflow.datadir`.

By default, :meth:`~workflow.workflow.Workflow.clear_data` will delete all the
files stored in :attr:`~workflow.workflow.Workflow.datadir`. It is used by the
``workflow:deldata`` and ``workflow:reset`` :ref:`magic arguments <magic-arguments>`.

It is possible to selectively delete files contained in the data directory by
supplying the optional ``filter_func`` callable. Please see :ref:`clearing-cache`
for details on how ``filter_func`` works.


.. _manual-settings:

Settings
========

:attr:`Workflow.settings <workflow.workflow.Workflow.settings>` is a subclass
of :class:`dict` that automatically saves its contents to the ``settings.json``
file in your Workflow's data directory when it is changed.

:class:`~workflow.workflow.Settings` can be used just like a normal :class:`dict`
with the caveat that all keys and values must be serializable to JSON.

.. warning::

    A :class:`~workflow.workflow.Settings` instance can only automatically
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
===============

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


.. _script-behaviour:

A note on Script Behaviour
==========================

In version 2.7, Alfred introduced a new Script Behaviour setting for
Script Filters. This allows you (among other things) to specify that a
running script should be killed if the user continues typing in Alfred.

If you enable this setting, it's possible that Alfred will terminate your
script in the middle of some critical code (e.g. writing a file).
Alfred-Workflow provides the :class:`~workflow.workflow.uninterruptible`
decorator to prevent your script being terminated in the middle of a
critical function.

Any function wrapped with :class:`~workflow.workflow.uninterruptible` will
be executed fully, and any signal caught during its execution will be
handled when your function completes.

For example:

.. code-block:: python
    :linenos:

    from workflow.workflow import uninterruptible

    @uninterruptible
    def critical_function():
         # Your critical code here

If you only want to write to a file, you can use the
:class:`~workflow.workflow.atomic_writer` context manager. This does not
guarantee that the file will be written, but does guarantee that it will
only be written if the write succeeds (the data is first written to a temporary
file).
