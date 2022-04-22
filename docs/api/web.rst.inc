
.. _api-web:

HTTP requests
-------------

.. module:: workflow.web

:mod:`workflow.web` provides a simple API for retrieving data from the Web
modelled on the excellent `requests`_ library.

The purpose of :mod:`workflow.web` is to cover trivial cases at just 0.5% of
the size of `requests`_.


.. autofunction:: get
.. autofunction:: post
.. autofunction:: request


Response objects
^^^^^^^^^^^^^^^^

.. autoclass:: Response
   :members:


.. _requests: http://docs.python-requests.org/en/latest/
