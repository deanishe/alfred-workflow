.. Alfred-Workflow documentation master file, created by
   sphinx-quickstart on Sun Mar  2 12:09:28 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _overview:

========
Overview
========

.. image:: https://img.shields.io/travis/deanishe/alfred-workflow/master.svg?style=flat
    :target: https://travis-ci.org/deanishe/alfred-workflow
    :alt: Build Status
.. image:: https://img.shields.io/coveralls/deanishe/alfred-workflow/master.svg?style=flat
    :target: https://coveralls.io/github/deanishe/alfred-workflow
    :alt: Code Coverage
.. :target: https://coveralls.io/r/deanishe/alfred-workflow?branch=master
.. .. image:: https://landscape.io/github/deanishe/alfred-workflow/master/landscape.png?style=flat
..     :target: https://landscape.io/github/deanishe/alfred-workflow/master
..     :alt: Code Health
.. image:: https://img.shields.io/pypi/v/Alfred-Workflow.svg?style=flat
    :target: https://pypi.python.org/pypi/Alfred-Workflow/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/status/Alfred-Workflow.svg?style=flat
    :target: https://pypi.python.org/pypi/Alfred-Workflow/
    :alt: Development Status
.. image:: https://img.shields.io/pypi/pyversions/Alfred-Workflow.svg?style=flat
    :target: https://pypi.python.org/pypi/Alfred-Workflow/
    :alt: Supported Python Versions
.. .. image:: https://img.shields.io/pypi/l/Alfred-Workflow.svg?style=flat
..     :target: https://pypi.python.org/pypi/Alfred-Workflow/
..     :alt: License
.. image:: https://img.shields.io/pypi/dm/Alfred-Workflow.svg?style=flat
    :target: https://pypi.python.org/pypi/Alfred-Workflow/
    :alt: Downloads


Go to :ref:`Quick Index <quickindex>`.


Alfred-Workflow is a Python helper library for `Alfred 2`_ workflow authors,
developed and hosted on `GitHub`_.

Alfred workflows typically take user input, fetch data from the Web or
elsewhere, filter them and display results to the user. Alfred-Workflow
takes care of a lot of the details for you, allowing you to concentrate your
efforts on your workflow's functionality.

Alfred-Workflow supports OS X 10.6+ (Python 2.6 and 2.7).


Features
========

- Catches and logs workflow errors for easier development and support
- :ref:`"Magic" arguments <magic-arguments>` to help development, debugging and
  management of the workflow
- :ref:`Auto-saves settings <manual-settings>`
- Super-simple :ref:`data caching <caching-data>`
- Fuzzy, :ref:`Alfred-like search/filtering <filtering>` with
  :ref:`diacritic folding <folding>`
- :ref:`Keychain support <keychain>` for secure storage (and syncing) of
  passwords, API keys etc.
- Simple generation of Alfred feedback (XML output)
- :ref:`Input/output decoding <text-encoding>` for handling non-ASCII text
- :ref:`Lightweight web <web>` API with `Requests`_-like interface
- Pre-configured logging
- Painlessly add directories to ``sys.path``
- Easily launch :ref:`background tasks <background-processes>` (daemons) to
  keep your workflow responsive
- :ref:`Check for and install new workflow versions <manual-updates>` using
  GitHub releases.
- :ref:`Post notifications <notifications>` with Notification Center (10.8+ only).



Quick example
=============

Here's how to show recent `Pinboard.in <https://pinboard.in/>`_ posts in Alfred.

Create a new workflow in Alfred's preferences. Add a **Script Filter** with
Language ``/usr/bin/python`` and paste the following into the **Script** field
(changing ``API_KEY``):

.. code-block:: python
    :linenos:
    :emphasize-lines: 4

    import sys
    from workflow import Workflow, ICON_WEB, web

    API_KEY = 'your-pinboard-api-key'

    def main(wf):
        url = 'https://api.pinboard.in/v1/posts/recent'
        params = dict(auth_token=API_KEY, count=20, format='json')
        r = web.get(url, params)
        r.raise_for_status()
        for post in r.json()['posts']:
            wf.add_item(post['description'], post['href'], arg=post['href'],
                        uid=post['hash'], valid=True, icon=ICON_WEB)
        wf.send_feedback()


    if __name__ == u"__main__":
        wf = Workflow()
        sys.exit(wf.run(main))


Add an **Open URL** action to your workflow with ``{query}`` as the **URL**,
connect your **Script Filter** to it, and you can now hit **ENTER** on a
Pinboard item in Alfred to open it in your browser.

.. warning::

    Using the above example code as a workflow will likely get
    you banned by the Pinboard API. See the :ref:`tutorial` if you want to
    build an API terms-compliant (and super-fast) Pinboard workflow.


Supported software
==================

Alfred-Workflow supports all versions of Alfred 2 and all versions of OS X
supported by Alfred 2. It works with Python 2.6 and 2.7, but *not* Python 3.

Some features are not available on older versions of OS X.

.. toctree::
  :maxdepth: 2

  supported-versions


Installation
============

Alfred-Workflow can be installed from the `Python Package Index`_ with
`pip`_ or from the source on `GitHub`_.

.. toctree::
    :maxdepth: 2

    installation



The Alfred-Workflow Tutorial
============================

A :ref:`two-part tutorial <tutorial>` on writing an Alfred workflow with
Alfred-Workflow, taking you through the basics to a performant and release-
ready workflow. This is the best starting point for workflow authors new to
Python or programming in general. More experienced Python coders should skim
this or skip straight ahead to the :ref:`user-manual`.

.. toctree::
    :maxdepth: 2

    tutorial



User Manual
===========

If you know your way around Python and Alfred, here's an overview of what
Alfred-Workflow can do and how to do it.

.. toctree::
   :maxdepth: 2

   user-manual/index


API documentation
=================

Documetation of the Alfred-Workflow APIs generated from the source code.
A handy reference if (like me) you sometimes forget parameter names.

.. toctree::
  :maxdepth: 2

  api/index



Script Filter results and the XML format
========================================

An in-depth look at Alfred's XML format, the many parameters accepted by
:meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>`
and how they interact with one another.

.. note::

    This should also serve as a decent reference to Alfred's XML format for
    folks who aren't using Alfred-Workflow. The official `Alfred 2 XML docs`_
    have recently seen a massive update, but historically haven't been very
    up-to-date.


.. toctree::
   :maxdepth: 3

   xml_format



Workflows using Alfred-Workflow
===============================

This is a list of some of the workflows based on Alfred-Workflow.

.. toctree::
   :maxdepth: 2

   aw-workflows



Feedback, questions, bugs, feature requests
===========================================

If you have feedback or a question regarding Alfred-Workflow, please post in
them in the `Alfred forum thread`_.

If you have a bug report or a feature request, please create a new
`issue on GitHub`_.

You can also email me at deanishe@deanishe.net with any questions/feedback/bug
reports. However, it's generally better to use the forum/GitHub so that other
users can benefit from and contribute to the conversation.


Quick Index
===========

The Quick Index is a list of links to all the interesting parts of the
documentation.

.. toctree::
    :maxdepth: 1

    quickindex


Indices and tables
==================

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`


.. _GitHub: https://github.com/deanishe/alfred-workflow/
.. _Requests: http://docs.python-requests.org/en/latest/
.. _Alfred 2: https://www.alfredapp.com/
.. _pip: https://pypi.python.org/pypi/pip
.. _Python Package Index: https://pypi.python.org/pypi/Alfred-Workflow
.. _Alfred forum thread: http://www.alfredforum.com/topic/4031-workflow-library-for-python/
.. _issue on GitHub: https://github.com/deanishe/alfred-workflow/issues
.. _Alfred 2 XML docs: https://www.alfredapp.com/help/workflows/inputs/script-filter