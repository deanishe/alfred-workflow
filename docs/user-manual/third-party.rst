
.. _thirdparty:

=============================
Including 3rd party libraries
=============================

It's a Very Bad Idea™ to install (or ask users to install) 3rd-party libraries
in the OS X system Python. Alfred-Workflow makes it easy to include them in
your Workflow.

Simply create a ``lib`` subdirectory under your Workflow's root directory
and install your dependencies there. You can call the directory whatever you
want, but in the following explanation, I'll assume you used ``lib``.

To install libraries in your dependencies directory, use:

.. code-block:: bash

    pip install --target=path/to/my/workflow/lib python-lib-name

The path you pass as the ``--target`` argument should be the path to
the directory under your Workflow's root directory in which you want to install
your libraries. ``python-lib-name`` should be the "pip name" (i.e. the name the
library has on `PyPI <https://pypi.python.org/pypi>`_) of the library you want
to install, e.g. ``requests`` or ``feedparser``.

This name is usually, but not always, the same as the name you use with ``import``.

For example, to install Alfred-Workflow, you would run
``pip install Alfred-Workflow`` but use ``import workflow`` to import it.

**An example:** You're in a shell in Terminal.app in the Workflow's root directory
and you're using ``lib`` as the directory for your Python libraries. You want to
install `requests <http://docs.python-requests.org/en/latest/>`_. You would run:

.. code-block:: bash

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

    from lib import requests

instead of simply:


.. code-block:: python

    import requests

