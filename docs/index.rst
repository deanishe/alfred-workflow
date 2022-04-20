
.. _overview:

==========================
Welcome to Alfred-Workflow
==========================

.. include:: badges.rst.inc

Go to :ref:`quickindex`.


Alfred-Workflow is a Python helper library for `Alfred 2, 3 and 4`_ workflow
authors, developed and hosted on `GitHub`_.

Alfred workflows typically take user input, fetch data from the Web or
elsewhere, filter them and display results to the user. Alfred-Workflow takes
care of a lot of the details for you, allowing you to concentrate your efforts
on your workflow's functionality.

Alfred-Workflow supports macOS Catalina or later.


Features
========

- Fuzzy, :ref:`Alfred-like search/filtering <filtering>` with
  :ref:`diacritic folding <folding>`
- :ref:`Simple, persistent settings <guide-settings>`
- Simple, auto-expiring :ref:`data caching <caching-data>`
- :ref:`Keychain support <keychain>` for secure storage (and syncing) of
  passwords, API keys etc.
- Simple generation of Alfred feedback (XML and JSON)
- :ref:`Lightweight web <guide-web>` API with `requests`_-like interface
- Easily launch :ref:`background tasks <background-processes>` (daemons) to
  keep your workflow responsive
- :ref:`Check for and install new workflow versions <guide-updates>` using
  GitHub releases
- :ref:`Post notifications <notifications>` with Notification Center
  (10.8+ only)
- Error handling and logging for easier development and support
- :ref:`"Magic" arguments <magic-arguments>` to help development,
  debugging and management of the workflow


Alfred 3+ features
------------------

- Set :ref:`workflows variables <workflow-variables>` from code
- Advanced modifiers
- Alfred version-aware updates (ignores incompatible updates)
- :ref:`Automatic re-running of Script Filters <guide-rerun>`.


Quick example
=============

Here's how to show recent `Pinboard.in <https://pinboard.in/>`_ posts in Alfred.

Create a new workflow in Alfred's preferences. Add a **Script Filter** with
Language ``/usr/bin/python3`` and paste the following into the **Script**
box (changing ``API_KEY``):

.. code-block:: python
    :linenos:
    :emphasize-lines: 4

    import sys
    from workflow import Workflow, ICON_WEB, web
    # To use Alfred 3+ feedback mechanism:
    # from workflow import Workflow3

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


.. include:: toc.rst.inc



.. _GitHub: https://github.com/deanishe/alfred-workflow/
.. _requests: http://docs.python-requests.org/en/latest/
.. _Alfred 2, 3 and 4: https://www.alfredapp.com/
