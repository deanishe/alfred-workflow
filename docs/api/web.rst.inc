
.. _api-web:

HTTP requests
-------------

.. module:: workflow.web

:mod:`workflow.web` provides a simple API for retrieving data from the Web
modelled on the excellent `requests`_ library.

The purpose of :mod:`workflow.web` is to cover trivial cases at just 0.5% of
the size of `requests`_.

.. danger::

    As :mod:`workflow.web` is based on Python 2's standard HTTP libraries,
    there are two important problems with SSL connections.

    Python versions older than 2.7.9 (i.e. pre-Yosemite) **do not**
    verify SSL certificates when establishing HTTPS connections.

    As a result, you **must not** use this module for sensitive
    connections unless you're certain it will only run on 2.7.9/Yosemite
    and later. If your workflow is Alfred 3-only, this requirement is met.

    Secondly, versions of macOS older than High Sierra (10.13) have an
    extremely outdated version of OpenSSL, which is incompatible with
    many servers' SSL configuration.

    Consequently, :mod:`workflow.web` cannot connect to such servers.
    As this includes GitHub's SSL configuration, the
    :ref:`update mechanism <guide-updates>` only works on High Sierra
    and later.


.. autofunction:: get
.. autofunction:: post
.. autofunction:: request


Response objects
^^^^^^^^^^^^^^^^

.. autoclass:: Response
   :members:


.. _requests: http://docs.python-requests.org/en/latest/
