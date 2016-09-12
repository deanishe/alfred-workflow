
.. _web:

Fetching Data from the Web
==========================

.. module:: workflow.web

:mod:`workflow.web` provides a simple API for retrieving data from the Web
modelled on the excellent `requests`_ library.

The purpose of :mod:`workflow.web` is to cover trivial cases at just 0.5% of
the size of `requests`_.

.. contents::
   :local:

Features
--------

- JSON requests and responses
- Form data submission
- File uploads
- Redirection support

The main API consists of the :func:`get` and :func:`post` functions and
the :class:`Response` instances they return.

.. warning::

    As :mod:`workflow.web` is based on Python 2's standard HTTP libraries,
    it **does not** verify SSL certificates when establishing HTTPS connections
    on Python versions older than 2.7.9 (i.e. pre-Yosemite).

    As a result, you **must not** use this module for sensitive
    connections unless you're certain it will only run on 2.7.9/Yosemite
    and later.

If you require certificate verification for HTTPS connections (which you
really should), you should use the excellent `requests`_ library
(upon which the :mod:`workflow.web` API is based) or the command-line tool
`cURL`_, which is installed by default on OS X, instead.


.. _web-examples:

Examples
--------

There are some examples of using :mod:`workflow.web` in other parts of the
documentation:

* :ref:`writing-script` in the :ref:`Tutorial <tutorial>`
* :ref:`web-data` in the :ref:`user-manual`



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
