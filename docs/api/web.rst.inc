
.. _api-web:

HTTP requests
-------------

.. module:: workflow.web

:mod:`workflow.web` provides a simple API for retrieving data from the Web
modelled on the excellent `requests`_ library.

The purpose of :mod:`workflow.web` is to cover trivial cases at just 0.5% of
the size of `requests`_.

.. warning::

    As :mod:`workflow.web` is based on Python 2's standard HTTP libraries,
    it **does not** verify SSL certificates when establishing HTTPS
    connections on Python versions older than 2.7.9 (i.e. pre-Yosemite).

    As a result, you **must not** use this module for sensitive
    connections unless you're certain it will only run on 2.7.9/Yosemite
    and later. If your workflow is Alfred 3-only, this requirement is met.


.. autofunction:: get
.. autofunction:: post
.. autofunction:: request


Response objects
^^^^^^^^^^^^^^^^

.. autoclass:: Response
   :members:


.. _requests: http://docs.python-requests.org/en/latest/
