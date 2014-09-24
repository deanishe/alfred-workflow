.. Alfred-Workflow documentation master file, created by
   sphinx-quickstart on Sun Mar  2 12:09:28 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _overview:

========
Overview
========

**Alfred-Workflow** is a Python helper library for
`Alfred 2`_ workflow authors, developed and hosted
on `GitHub`_.

Alfred workflows typically take user input, fetch data from the Web or
elsewhere, filter them and display results to the user. **Alfred-Workflow**
takes care of a lot of the details for you, allowing you to concentrate your
efforts on your workflow's functionality.

.. note::

    **Alfred-Workflow** is *the only library* that supports all of Alfred 2's
    features (as of version 2.5 of Alfred, version 1.8.5 of **Alfred-Workflow**).



Features
========

- Catches and logs workflow errors for easier development and support
- :ref:`"Magic" arguments <magic-arguments>` to help development/debugging
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
- :ref:`Check for new versions <manual-updates>` and update workflows hosted on
  GitHub.



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



Installation
============

**Alfred-Workflow** can be installed from the `Python Package Index`_ with
`pip`_ or from the source on `GitHub`_.

.. toctree::
    :maxdepth: 2

  installation



The Alfred-Workflow Tutorial
============================

A :ref:`two-part tutorial <tutorial>` on writing an Alfred workflow
with **Alfred-Workflow**, taking you through the basics to a full-featured
workflow. This is the best starting point for workflow authors new to Python
or programming in general. More experienced Python coders should skim this
or skip straight ahead to the :ref:`user-manual`.

.. toctree::
    :maxdepth: 2

    tutorial



User Manual
===========

If you know your way around Python and Alfred, here's an overview of what
**Alfred-Workflow** can do and how to do it.

.. toctree::
   :maxdepth: 2

   user-manual/index


API documentation
=================

Detailed documetation of the **Alfred-Workflow** APIs, detailing the full API.

.. toctree::
  :maxdepth: 2

  api/index



Script Filter results and the XML format
----------------------------------------

An in-depth look at the many parameters accepted by
:meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>`
and how they interact with one another.

This should also serve as a decent reference to Alfred's XML format for folks
who aren't using **Alfred-Workflow**. The official Alfred 2 documentation is
scattered, incomplete, out-of-date, and in places, simply incorrect.

I make no guarantees for the correctness or completeness of this documentation,
but it's currently (as of Alfred version 2.5) more accurate and complete than
the official documentation. Additions and corrections welcome.

.. toctree::
   :maxdepth: 3

   xml_format



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


.. _GitHub: https://github.com/deanishe/alfred-workflow/
.. _Requests: http://docs.python-requests.org/en/latest/
.. _Alfred 2: http://www.alfredapp.com/
.. _pip: https://pypi.python.org/pypi/pip
.. _Python Package Index: https://pypi.python.org/pypi/Alfred-Workflow
