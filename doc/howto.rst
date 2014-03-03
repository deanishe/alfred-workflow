
=========================
Using **Alfred-Workflow**
=========================

This document serves as a quick-reference/recipe book for the features of
**Alfred-Python**.

If you're new to writing Workflows or coding in general, start with the
:ref:`Tutorial <tutorial>`.

Writing a Workflow with **Alfred-Python**
-----------------------------------------

**Alfred-Python** is aimed particularly at authors of so-called
**Script Filters**. These are activated by a keyword in Alfred, receive
user input and return results to Alfred.

To create a **Script Filter** in Alfred, make sure your **Script Filter**
is set to use ``/bin/bash`` as the **Language**, and select the
following (and only the following) **Escaping** options:

- Backquotes
- Double Quotes
- Dollars
- Backslashes

The **Script** field should contain the following::

    python yourscript.py "{query}"


where ``yourscript.py`` is the name of your script.

Your workflow should start out like this. This enables :class:`Workflow`
to capture any errors thrown by your scripts::

    #!/usr/bin/python
    # encoding: utf-8

    import sys

    from workflow import Workflow


    def main(wf):
        # The Workflow instance will be passed to the function
        # you call from `Workflow.run`
        # Your imports here if you want to catch import errors
        import somemodule
        import anothermodule
        # Get args from Workflow, already in normalised Unicode
        args = wf.args

        # Do stuff here ...

        # Add an item to Alfred feedback
        wf.add_item(u'Item title', u'Item subtitle')

        # Send output to Alfred
        wf.send_feedback()


    if __name__ == '__main__':
        wf = Workflow()
        sys.exit(wf.run(main))


.. _magic-arguments:

"Magic" arguments
-----------------

If your Script Filter (or script) accepts a query, you can pass it so-called
magic arguments that instruct :class:`~workflow.workflow.Workflow` to perform
certain actions, such as opening the log file or clearing the cache/settings.

These can be a big help while developing and debugging and especially when
debugging problems your Workflow's users may be having.

The :meth:`~workflow.workflow.Workflow.run` method of
:class:`~workflow.workflow.Workflow` (which you should "wrap" your Workflow's
entry functions in) will catch any raised exceptions, log them and display
them in Alfred. You can call your Workflow with ``workflow:openlog`` as an
Alfred query/command line argument and :class:`~workflow.workflow.Workflow`
will open the Workflow's log file in the default app (usually **Console.app**).

This makes it easy for you to get at the log (hidden away in ``~/Library``) and
for your users to send you their logs for debugging.

:class:`~workflow.workflow.Workflow` supports the following "magic" args:

- ``workflow:openlog`` — open the Workflow's log file in the default app.
- ``workflow:delcache`` — delete any data cached by the Workflow.
- ``workflow:delsettings`` — delete the Workflow's settings file (the data saved using :attr:`~workflow.workflow.Workflow.settings`).