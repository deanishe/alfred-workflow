
.. _workflow-variables:

==================
Workflow variables
==================

**Alfred 3+ only**

.. currentmodule:: workflow.workflow3

An extremely powerful new feature in Alfred 3 is `its workflow variables`_.

Alfred exposes these to your workflow as environment variables, and you can
set and manipulate these not only in Alfred's own UI elements, but
also via the output from a Run Script action or Script Filter results.

Any variables set via the JSON output of a Run Script or Script Filter
only persist as long as the workflow is running. When the workflow is
run again, the variables reset to the initial values set in the
workflow configuration sheet.

Alfred 3.6 introduced a new API to update the values stored in the `workflow
configuration sheet`_, i.e. the values persist across workflow runs.


.. important::

    You must use the correct mechanism for setting variables. Alfred
    requires different output formats from Script Filters and Run Script
    actions, and if you use the wrong one, it won't work.


The two different mechanisms for setting workflow variables are:

* The :class:`~workflow.Variables` class, which is for use in
  **Run Script** actions, and
* The :class:`~workflow.Workflow3` class provides an
  API for getting and setting workflow variables via **Script Filter**
  feedback.


.. contents::
   :local:


.. _variables-getting:

Getting variables
=================

Alfred-Workflow does not automatically import any variables. All getters
only consider variables you have set on the objects yourself, not those
set by upstream workflow elements or the `workflow configuration sheet`_.

The reason for this is that Alfred-Workflow cannot distinguish between
workflow variables and real environment variables.

For example, if you call ``os.getenv('HOME')``, you will get the user's
home directory, but ``{var:HOME}`` will not work in Alfred elements.

By restricting its scope to variables it has set itself, Alfred-Workflow
can guarantee that if ``getvar('xyz')`` works, ``{var:xyz}`` will also
work in downstream Alfred elements.


.. _variables-run-script:

Setting variables from Run Script actions
=========================================

:class:`~workflow.Variables` is a subclass of :class:`dict` that
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


.. _variables-script-filter:

Setting variables in Script Filters
===================================

Variables can be set at the Workflow, Item or Modifier level using their
respective ``setvar(name, value)`` methods. Variables set on the
:class:`~workflow.Workflow3` object are hereafter referred to as "top-level"
variables. :meth:`~workflow.Workflow3.setvar` takes an additional, optional
``persist`` argument, which will also save the variable to ``info.plist``/
the `workflow configuration sheet`_. As this requires calling Alfred via
AppleScript (which is slow), it's generally a better option to save variables
further downstream in a non-interactive part of the workflow. See
:ref:`variables-persistent` for more information.

.. note::

    Top-level variables are also passed back to your Script Filter when you're
    using Alfred's :ref:`rerun <guide-rerun>` feature. This is extremely handy
    for creating timers or progress bars.

Alfred-Workflow imposes its own logic for setting variables that differs
from the way Alfred handles them.

:class:`Item3` and :class:`Modifier` objects inherit any variables
set on their parent object (:class:`~workflow.Workflow3` and :class:`Item3`
respectively) *at the time of their creation* via
:meth:`Workflow3.add_item() <workflow.Workflow3.add_item>` and
:meth:`Item3.add_modifier`.

This way, you can have some variables inherited and some not.

The validity and ``arg`` of the modifier will be the same as the parent
item's, so you only need to specify ``valid`` or ``arg`` if you wish to
override the parent item's value.

.. important::

    The way Alfred handles variables is somewhat arbitrary. Top-level
    variables are also passed downstream with any item-level variables,
    regardless of whether the item sets its own variables.

    If a modifier sets any variables, however, Alfred ignores any top-
    and item-level variables completely.

    The upshot for Alfred-Workflow is that top-level variables will also
    be passed along with items created *before* the variables were set,
    but *not* with modifiers created before the variables were set.


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

    /usr/bin/python3 myscript.py pages


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


.. currentmodule:: workflow

.. _variables-persistent:

Persisting variables
====================

As a convenience, the :meth:`Workflow3.setvar` method takes an optional
``persist`` argument, which will also save the variable to
``info.plist``/the `workflow configuration sheet`_, but this method is
generally sub-optimal, as it immediately calls Alfred via AppleScript,
which is slow.

The better method for saving variables is the :func:`util.set_config`
function (and its :func:`util.unset_config` counterpart).

Ideally, you should call these functions downstream of any interactive
elements (e.g. Script Filters), as calling Alfred via AppleScript is
slow.

.. code-block:: python
    :linenos:

    import os
    from workflow.util import set_config

    # Retrieve the current value from the environment
    current = int(os.getenv('SOME_COUNT') or '0')

    # Increment value and save back to Alfred
    set_config('SOME_COUNT', str(current + 1))

You can also save variables to other workflows by specifying its
bundle ID by passing ``bundleid="XYZ"`` to :func:`util.set_config`.


More information
================

Alfred's own help has a `few`_ `pages`_ on workflow variables.

Also see this guide to `getting, setting and saving workflow variables`_.


.. _workflow configuration sheet: https://www.alfredapp.com/help/workflows/advanced/variables/#environment
.. _its workflow variables: https://www.alfredapp.com/help/workflows/utilities/argument/
.. _few: https://www.alfredapp.com/help/workflows/utilities/argument/
.. _pages: https://www.alfredapp.com/help/workflows/advanced/variables/
.. _getting, setting and saving workflow variables: https://www.deanishe.net/post/2018/10/workflow/environment-variables-in-alfred/

.. _Click: http://click.pocoo.org/
