
.. _web:

Fetching Data from the Web
==========================

.. module:: workflow.web

:mod:`workflow.web` provides a simple API for retrieving data from the Web
modelled on the excellent `requests`_ library.

The purpose of :mod:`workflow.web` is to cover trivial cases at just 0.5% of
the size of `requests`_.

Features:

- JSON requests and responses
- Form data submission
- File uploads
- Redirection support

The main API consists of the :func:`get` and :func:`post` functions and
the :class:`Response` instances they return.

.. warning::

    As :mod:`workflow.web` is based on Python 2's standard HTTP libraries, it
    **does not** verify SSL certificates when establishing HTTPS
    connections.

    As a result, you **must not** use this module for sensitive
    connections.

If you require certificate verification for HTTPS connections (which you
really should), you should use the excellent `requests`_ library
(upon which the :mod:`workflow.web` API is based) or the command-line tool
`cURL`_, which is installed by default on OS X, instead.


Examples
--------

There are some examples of using :mod:`workflow.web` in other parts of the
documentation:

* :ref:`writing-script` in the :ref:`Tutorial <tutorial>`
* :ref:`web-data` in the :ref:`quickref`

The `unit tests`_ contain examples of pretty
much everything :mod:`workflow.web` can do:

* `GET`_ and `POST`_ variables
* `Retrieve and decode JSON`_
* `Post JSON`_
* `Post forms`_
* Automatically handle encoding for `HTML`_ and `XML`_
* `Basic authentication`_
* File uploads `with forms`_ and `without forms`_
* `Download large files`_
* `Variable timeouts`_
* `Ignore redirects`_


API
---

:func:`get` and :func:`post` are wrappers around :func:`request`. They all
return :class:`Response` objects.

.. autofunction:: get
.. autofunction:: post
.. autofunction:: request

The Response object
^^^^^^^^^^^^^^^^^^^

.. autoclass:: Response
   :members:

.. _requests: http://docs.python-requests.org/en/latest/
.. _cURL: http://curl.haxx.se/
.. _GET: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L128
.. _POST: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L76
.. _unit tests: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py
.. _Ignore redirects: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L67
.. _Variable timeouts: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L101
.. _Post forms: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L76
.. _Post JSON: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L86
.. _HTML: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L106
.. _XML: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L121
.. _Basic authentication: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L137
.. _with forms: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L153
.. _without forms: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L173
.. _Retrieve and decode JSON: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L189
.. _Download large files: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L197

