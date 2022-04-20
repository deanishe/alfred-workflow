
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

    /usr/bin/python3 yourscript.py "{query}"


where ``yourscript.py`` is the name of your script [#]_.

Your workflow should start out like this. This enables :class:`Workflow`
to capture any errors thrown by your scripts:

.. code-block:: python
    :linenos:

    #!/usr/bin/python3
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


.. [#] It's better to specify ``/usr/bin/python3`` over just ``python``. This
       ensures that the script will always be run with the system default
       Python regardless of what ``PATH`` might be.
