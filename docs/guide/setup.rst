
.. _setup:

===========================
Workflow setup and skeleton
===========================

Alfred-Workflow is aimed particularly at authors of so-called
**Script Filters**. These are activated by a keyword in Alfred, receive
user input and return results to Alfred.

To write a Script Filter with Alfred-Workflow, make sure your Script Filter
is set to use ``/bin/bash`` as the **Language**, and select the
following (and only the following) **Escaping** options:

- Backquotes
- Double Quotes
- Dollars
- Backslashes

The **Script** field should contain the following::

    /usr/bin/env python yourscript.py "{query}"


where ``yourscript.py`` is the name of your script [#]_.

Your workflow should start out like this. This enables :class:`Workflow`
to capture any errors thrown by your scripts:

.. code-block:: python
    :linenos:

    #!/usr/bin/env python
    # encoding: utf-8

    import sys

    from workflow import Workflow

    log = None


    def main(wf):
        # The Workflow instance will be passed to the function
        # you call from `Workflow.run`

        # Your imports here if you want to catch import errors
        import somemodule
        import anothermodule

        # Get args from Workflow as normalized Unicode
        args = wf.args

        # Do stuff here ...

        # Add an item to Alfred feedback
        wf.add_item('Item title', 'Item subtitle')

        # Send output to Alfred
        wf.send_feedback()


    if __name__ == '__main__':
        wf = Workflow()
        # Assign Workflow logger to a global variable for convenience
        log = wf.logger
        sys.exit(wf.run(main))

**Important note**: Python 2 was `removed in macOS 12.3 <https://developer.apple.com/documentation/macos-release-notes/macos-12_3-release-notes#:~:text=Python%202.7%20was%20removed%20from%20macOS%20in%20this%20update>`_. Users that run macOS 12.3 or newer will have to `install Python 2.7.18 manually <https://www.python.org/downloads/release/python-2718/>`_.
Additionally, the following code needs to be added to the ``info.plist`` file after ``<plist><dict>``:

.. code-block:: xml
    :linenos:

    <key>variables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/Library/Frameworks/Python.framework/Versions/2.7/bin</string>
    </dict>

This is required because Alfred doesn't inherit environment variables and doesn't source shell configuration files (such as `.zshrc`).


.. [#] It's better to specify ``/usr/bin/env python`` over just ``python``. This
       ensures that the script will always be found.