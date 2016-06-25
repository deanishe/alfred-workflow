
.. _workflow-variables:

==================
Workflow variables
==================

An extremely powerful new feature in Alfred 3 is `its workflow variables`_.

You can set and manipulate these not only in Alfred's own UI elements, but
also via script output or Script Filter results.

The Alfred 3-only :class:`~workflow.workflow3.Workflow3` class provides an
API for getting and setting workflow variables via Script Filter feedback
output.

Variables can be set at the Workflow, Item or Modifier level using their
respective ``setvar(name, value)`` methods.

Items and Modifiers inherit any variables set on their parent Workflow or Item
objects *at the time of their creation*.

This way, you can have some variables inherited and others not.


.. important::

    Alfred-Workflow does not automatically import any variables. All getters
    only consider variables you have set, not those passed to your script by
    Alfred.


Example usage
-------------

As Alfred passes workflow variables to scripts as environment variables,
combining ``var=1`` style flags with a command-line library that can
map environment variables to command-line options (such as `Click`_) is
a clean and powerful idiom.

Click allows you to set a prefix, e.g. ``WF_``, and it will then automatically
map matching environment variables to corresponding command-line options, e.g.
``WF_USERNAME=deanishe`` is equivalent to ``--username=deanishe`` and
``wF_DEBUG=1`` is equivalent to ``--debug``.

Let's say we're using a client program for some imaginary social whatnot that
works like this::

    prog [--username=<name>] (profile|pages|friends) (--view|--edit|--share)


You could control this program from a Script Filter as follows. This assumes
you would connect the Script Filter to three Run Script Actions, one for
each of ``profile``, ``pages`` and ``friends``, and with a Filter Utility
before each Run Script that checks for ``pages == 1``, ``profile == 1`` etc.

.. code-block:: python
    :linenos:

    from workflow import Workflow3
    wf = Workflow3()

    # Username will be needed in every case. Set at the workflow level
    # to ensure all items inherit it
    wf.setvar('WF_USERNAME', 'deanishe')

    # Some example actions. We've set username above as the main
    # identifier. We'll set flags on feedback items that subsequent workflow
    # Filter Utilities can use and WF_* variables to pass arguments
    # directly to the program

    # Profile
    it = wf.add_item('Profile', 'View profile', arg='profile', valid=True)
    # Inherited by all modifiers
    it.setvalue('profile', '1')

    mod = it.add_modifier('cmd', 'Edit profile')
    # Set only on mod
    mod.setvalue('WF_EDIT', '1')

    mod = it.add_modifier('alt', 'Share profile')
    # Set only on mod
    mod.setvalue('WF_SHARE', '1')

    # Set after modifier creation, so only set on item
    it.setvalue('WF_VIEW', '1')

    # Pages
    it = wf.add_item('Pages', 'View pages', arg='pages', valid=True)
    # Inherited by all modifiers
    it.setvalue('pages', '1')

    mod = it.add_modifier('cmd', 'Edit pages')
    # Set only on mod
    mod.setvalue('WF_EDIT', '1')

    mod = it.add_modifier('alt', 'Share pages')
    # Set only on mod
    mod.setvalue('WF_SHARE', '1')

    # Set after modifier creation, so only set on item
    it.setvalue('WF_VIEW', '1')

    # Repeat for Friends
    # ...
    # ...


More information
----------------

Alfred's own help has a `few`_ `pages`_ on workflow variables.

`Here`_ is a post I wrote on the Alfred forums about getting, setting and
saving workflow variables.


.. _its workflow variables: https://www.alfredapp.com/help/workflows/utilities/argument/
.. _few: https://www.alfredapp.com/help/workflows/utilities/argument/
.. _pages: https://www.alfredapp.com/help/workflows/advanced/variables/
.. _Here: http://www.alfredforum.com/topic/9070-how-to-workflowenvironment-variables/

.. _Click: http://click.pocoo.org/
