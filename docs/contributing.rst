
.. _contributing:

============
Contributing
============

Alfred-Workflow is an open-source project and contributions are welcome.

.. important::

    **Do not submit yet another feature request for Python 3 support**

    I am aware of the existence of Python 3. There will be a rewrite of the library that removes all the crufy and only supports Python 3 when I get around to it.


.. _bugs:

Feature requests and bugs
=========================

If you have a bug report or a feature request, please create a new
`issue on GitHub`_.


.. _pull-requests:

Pull requests
=============

If you'd like to submit a pull request, please observe the following:

- Alfred-Workflow has very close to 100% test coverage. "Proof-of-concept"
  pull requests without tests are welcome. However, please be prepared
  to add the appropriate tests if you want your pull request to be ultimately
  accepted.
- Complete coverage is *only a proxy* for decent tests. Tests should also
  cover a decent variety of valid/invalid input. For example, if the code
  *could potentially* be handed non-ASCII input, it should be tested with
  non-ASCII input.
- Code should be `PEP8`_-compliant as far as is reasonable. Any decent code
  editor has a PEP8 plugin that will warn you of potential transgressions.
- Please choose your function, method and argument names carefully, with an
  eye to the existing names. Obviousness is more important than brevity.
- Document your code using the `Sphinx ReST format`_. Even if your
  function/method isn't user-facing, some other developer will be looking at
  it. Even if it's only a one-liner, the developer may be looking at
  :ref:`the API docs <api>` in a browser, not at the source code.
  If you don't feel comfortable writing English, I'd be happy to write the
  docs for you, but please ensure the code is easily understandable (i.e. comment the code if it's not totally obvious).
- Performance counts. By default, Alfred will try to run a workflow anew on
  every keypress. As a rule, 0.3 seconds execution time is decent, 0.2
  seconds or less is smooth. Alfred-Workflow should do its utmost to
  consume as little of that time as possible.

The main entry point for unit testing is the ``run-tests.sh`` script in the root directory. This will fail *if code coverage is < 100%*. Travis-CI and GitHub Actions also use this script. Add ``# pragma: no cover`` with care.


.. _unit-tests:

Unit tests
==========

Alfred-Workflow includes a full suite of unit tests. Please use the
``run-tests.sh`` script in the root directory of the repo to run the unit tests: it creates the necessary test environment to run the unit tests.
``test_workflow.py`` *will* fail if not run via ``run-scripts.sh``, but the test suites for the other modules may also be run directly.

Moreover, ``run-tests.sh`` checks the coverage of the unit tests and will fail if it is below 100%.


.. _questions:

Questions and help
==================

If you have feedback or a question regarding Alfred-Workflow, please post in
the `Alfred forum thread`_.



.. _Alfred forum thread: http://www.alfredforum.com/topic/4031-workflow-library-for-python/
.. _GitHub: https://github.com/deanishe/alfred-workflow/
.. _Python Package Index: https://pypi.python.org/pypi/Alfred-Workflow
.. _issue on GitHub: https://github.com/deanishe/alfred-workflow/issues
.. _pip: https://pypi.python.org/pypi/pip
.. _PEP8: http://legacy.python.org/dev/peps/pep-0008/
.. _Sphinx ReST format: http://sphinx-doc.org/
