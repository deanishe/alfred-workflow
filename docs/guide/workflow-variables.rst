
.. _workflow-variables:

==================
Workflow variables
==================

**Alfred 3 only**

An extremely powerful new feature in Alfred 3 is `its workflow variables`_.

You can set and manipulate these not only in Alfred's own UI elements, but
also via the output from a Run Script action or Script Filter results.


.. important::

    You must use the correct mechanism for setting variables. Alfred
    requires different output formats from Script Filters and Run Script
    actions, and if you use the wrong one, it won't work.


The two different mechanisms for setting workflow variables are:

* The :class:`~workflow.workflow3.Variables` class, which is for use in
  **Run Script** actions, and
* The :class:`~workflow.Workflow3` class provides an
  API for getting and setting workflow variables via **Script Filter**
  feedback.


.. _variables-run-script:

Setting variables from Run Script actions
=========================================

:class:`~workflow.workflow3.Variables` is a subclass of :class:`dict` that
serialises (prints) to an ``alfredworkflow`` JSON object (or plain text if no
variables are set).

Set workflow variables using the standard :class:`dict` API or as keyword
arguments on instantiation.


Example usage
-------------

.. code-block:: python
    :linenos:

    from __future__ import print_function
    from workflow import Variables

    # set arg on instantiation
    v = Variables(u'this is arg')

    # set workflow variables on instantiation
    v = Variables(var1=u'value 1', var2=u'value 2')

    # set arg via attribute
    v = Variables()
    v.arg = u'this is arg'

    # set workflow variables via dict API
    v = Variables()
    v['variable_name'] = u'variable value'

    # set config for downstream element
    v = Variables()
    v.config['key'] = u'value'

    # send to Alfred
    v = Variables(u'arg', var1='val1', var2='var2')
    print(v)


Setting variables in Script Filters
===================================

Variables can be set at the Workflow, Item or Modifier level using their
respective ``setvar(name, value)`` methods.

Variables set on the :class:`~workflow.Workflow3` object are
"global", as they are emitted as part of the top-level feedback object sent to
Alfred. They are always passed to downstream workflow objects regardless of
which item the user actions (and indeed, even if the user doesn't action any
result: they are also used by Alfred for its :ref:`rerun <guide-rerun>`
feature).

Variables set at the
:class:`Item <workflow.workflow3.Item3>`/:class:`~workflow.workflow3.Modifier`
level are only set if the user actions that item (and modifier).


Inheritance
-----------

:class:`Modifiers <workflow.workflow3.Modifier>` inherit any variables set on
their parent :class:`~workflow.workflow3.Item3` objects *at the time of their
creation*. Any variables set on an :class:`~workflow.workflow3.Item3` object
*after* a :class:`~workflow.workflow3.Modifier` was added are *not* inherited
by the modifier.

This way, you can have some variables inherited and others not.

Modifiers also inherit the validity of their parent item (so you only
need to supply a ``valid`` parameter to override the parent).

They *do not* inherit their parent item's ``arg``.


.. important::

    Alfred-Workflow does not automatically import any variables. All getters
    only consider variables you have set on the objects yourself, not those
    set by upstream workflow elements or the configuration sheet.


.. _example-variables:

Example usage
-------------

As Alfred passes workflow variables to scripts as environment variables,
combining ``var=1`` style flags with a command-line library that can
map environment variables to command-line options (such as `Click`_) is
a clean and powerful idiom.

Click allows you to set a prefix, e.g. ``WF_``, and it will then automatically
map matching environment variables to corresponding command-line options, e.g.
``WF_USERNAME=deanishe`` is equivalent to ``--username=deanishe`` and
``WF_DEBUG=1`` is equivalent to ``--debug``.

Let's say we're using a client program for some imaginary social whatnot that
works like this::

    prog [--username=<name>] (profile|pages|friends) (--view|--edit|--share)


You could control this program from a Script Filter as follows. This assumes
you would connect the Script Filter to three Run Script Actions, one for
each of ``profile``, ``pages`` and ``friends``, and with a Filter Utility
before each Run Script that checks for ``pages == 1``, ``profile == 1`` etc.

The Run Script action behind the ``pages == 1`` Filter Utility might then
read:

.. code-block:: bash

    /usr/bin/python myscript.py pages


The other options (``--view``, ``--edit``, ``--share``) are set via the
corresponding environment variables (``WF_VIEW``, ``WF_EDIT`` and ``WF_SHARE``
respectively).

The salient part of the Script Filter driving the workflow might look
like this:

.. code-block:: python
    :linenos:

    from workflow import Workflow3
    wf = Workflow3()

    # Username will be needed in every case. Set at the workflow level
    # to ensure it is always passed to downstream workflow objects
    wf.setvar('WF_USERNAME', 'deanishe')

    # Some example actions. We've set username above as the main
    # identifier. We'll set flags on feedback items that subsequent workflow
    # Filter Utilities can use and WF_* variables to pass arguments
    # directly to the program

    # Profile
    it = wf.add_item('Profile', 'View profile', arg='profile', valid=True)
    # Inherited by all modifiers
    it.setvar('profile', '1')

    mod = it.add_modifier('cmd', 'Edit profile')
    # Set only on mod. Equivalent to option --edit
    mod.setvar('WF_EDIT', '1')

    mod = it.add_modifier('alt', 'Share profile')
    # Set only on mod. Equivalent to option --share
    mod.setvar('WF_SHARE', '1')

    # Set after modifier creation, so only set on item, and is thus the default
    # Equivalent to option --view
    it.setvar('WF_VIEW', '1')

    # Pages
    it = wf.add_item('Pages', 'View pages', arg='pages', valid=True)
    # Inherited by all modifiers
    it.setvar('pages', '1')

    mod = it.add_modifier('cmd', 'Edit pages')
    # Set only on mod. Equivalent to option --edit
    mod.setvar('WF_EDIT', '1')

    mod = it.add_modifier('alt', 'Share pages')
    # Set only on mod. Equivalent to option --share
    mod.setvar('WF_SHARE', '1')

    # Set after modifier creation, so only set on item, and is thus the default
    # Equivalent to option --view
    it.setvar('WF_VIEW', '1')

    # Repeat for Friends
    # ...
    # ...


.. tip::
    While you could also replace the ``(view|edit|friends)`` commands with
    a ``--command (view|edit|friends)`` option and drive the whole workflow
    via environment/workflow variables, I'd advise against going too far in
    that direction (e.g. having a single Script Filter connected to a single
    Run Action containing an option-less command), as it could make your
    workflow very hard to follow for people wanting to hack on it.


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
