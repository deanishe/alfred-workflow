
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

    data = wf.cached_data('stuff', max_age=600)

.. note:: This will return ``None`` if there are no corresponding data in the cache.

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
