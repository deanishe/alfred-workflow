
.. _script-filter-results:

====================================
Script Filter results and XML format
====================================

.. note::
    This document is valid as of version 2.4 of Alfred and 1.8.5 of
    **Alfred-Workflow**.

Alfred's Script Filters are its most powerful workflow API and a main focus
of **Alfred-Workflow**. Script Filters work by receiving a ``{query}`` from
Alfred and returning a list of results as an XML file.

To build this list of results use the :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>`
method, and then :meth:`Workflow.send_feedback() <workflow.workflow.Workflow.send_feedback>`
to send the results back to Alfred.

This document is an attempt to explain how the many options available in the
XML format and :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>`'s
arguments work.

.. danger::
   As Script Filters use ``STDOUT`` to send their results to Alfred
   as XML, you **must not** :func:`print` or log any output to ``STDOUT`` or it
   will break the XML, and Alfred will show no results.

.. _xmlformat:

The XML format
==============

**Note:** If you're not using **Alfred-Workflow** to generate your XML, you should use a
real XML library to do so. It looks simple, but there are a lot of characters that
XML doesn't like, so it's much safer and more reliable to use a proper XML-generation
library than to try and cobble it together yourself.

This is a valid and complete list of results containing just one result with all
possible options. :meth:`Workflow.send_feedback() <workflow.workflow.Workflow.send_feedback>`
will print something much like this to ``STDOUT`` when called (though it won't be as pretty
as it will all be on one line).

.. _xml-example:

.. code-block:: xml
    :linenos:

    <?xml version="1.0" encoding="UTF-8"?>
    <items>
        <item uid="home" valid="YES" autocomplete="Home Folder" type="file">
            <title>Home Folder</title>
            <subtitle>Home folder ~/</subtitle>
            <subtitle mod="shift">Subtext when shift is pressed</subtitle>
            <subtitle mod="fn">Subtext when fn is pressed</subtitle>
            <subtitle mod="ctrl">Subtext when ctrl is pressed</subtitle>
            <subtitle mod="alt">Subtext when alt is pressed</subtitle>
            <subtitle mod="cmd">Subtext when cmd is pressed</subtitle>
            <text type="copy">Text when copying</text>
            <text type="largetype">Text for LargeType</text>
            <icon type="fileicon">~/</icon>
            <arg>~/</arg>
        </item>
    </items>

The first line is the standard XML declaration. You should probably stick with
one exactly as shown here and ensure your XML is encoded as UTF-8 text.

The root element **must** be ``<items>`` (lines 2 and 16).

The ``<items>`` element should contain one or more ``<item>`` elements.

To generate the above XML with **Alfred-Workflow** you would do:

.. _code-example:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    wf = Workflow()

    wf.add_item(u'Home Folder',     # title
                u'Home folder ~/',  # subtitle
                modifier_subtitles={
                    u'shift': u'Subtext when shift is pressed',
                    u'fn': u'Subtext when fn is pressed',
                    u'ctrl': u'Subtext when ctrl is pressed',
                    u'alt': u'Subtext when alt is pressed',
                    u'cmd': u'Subtext when cmd is pressed'
                },
                arg=u'~/',
                autocomplete=u'Home Folder',
                valid=True,
                uid=u'home',
                icon=u'~/',
                icontype=u'fileicon',
                type=u'file',
                largetext=u'Text for LargeType',
                copytext=u'Text when copying')

    # Print XML to STDOUT
    wf.send_feedback()

Result items
------------

A minimal, valid result looks like this:

.. code-block:: xml
    :linenos:

    <item>
        <title>My super title</title>
    </item>

Generated with:

.. code-block:: python
    :linenos:

    wf.add_item(u'My super title')

This will show a result in Alfred with Alfred's blank workflow icon and 'My super title'
as its text.

Everything else is optional, but some attributes/child tags don't make much sense on their
own. We'll ignore the difference between whether a parameter is an attribute on the
``<item>`` tag or a child tag and look at what they do.


.. _param-title:

title
^^^^^

This is the large text shown for each result in Alfred's results list.

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``title`` argument or the first unnamed argument. This is the only
required argument and must be :class:`unicode`:

.. code-block:: python
    :linenos:

    wf.add_item(u'My title'[, ...])

or

.. code-block:: python
    :linenos:

    wf.add_item(title=u'My title'[, ...])

.. _param-subtitle:

subtitle
^^^^^^^^

This is the smaller text shown under each result in Alfred's results list.
Remember that users can turn off subtitles in Alfred's settings.

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``subtitle`` argument or the second unnamed argument (the first, ``title``,
is required, and must therefore be present.

It's also possible to specify custom subtitles to be shown when a result is
selected and the user presses one of the modifier keys (⌘,⌥, ^, ⇧, fn).

These are specified in the XML file as additional ``<subtitle>`` elements with
``mod="<key>"`` attributes (see lines 6–10 in the
:ref:`example XML <xml-example>`).

In **Alfred-Workflow**, you can set modifier-specific subtitles with the
``modifier_subtitles`` argument to
:meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>`, which must
be a dictionary with some or all of the keys ``alt``, ``cmd``, ``ctrl``,
``fn``, ``shift`` and the corresponding values set to the :class:`unicode`
subtitles to be shown when the modifiers are pressed (see lines 7–13 of the
:ref:`example code <code-example>`).

.. _param-autocomplete:

autocomplete
^^^^^^^^^^^^

If the user presses ``TAB`` on a result, the query currently shown in Alfred's
query box will be expanded to the ``autocomplete`` value of the selected result.

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``autocomplete`` argument. Must be :class:`unicode`.

When a user autocompletes a result with ``TAB``, Alfred will run the workflow
again with the new query.

.. _param-arg:

arg
^^^

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``arg`` argument. Must be :class:`unicode`.

This is the "value" of the result which will be passed by Alfred as ``{query}``
to the Action(s) or Output(s) your Script Filter is connected to.

Additionally, if you press ⌘+C on a result in Alfred, ``arg`` will be copied to
the pasteboard (unless you have set :ref:`copy text <param-copytext>` for the
item).

Other than being copyable, setting ``arg`` doesn't make great deal of sense unless
the item is also :ref:`valid <param-valid>`.

**Note:** ``arg`` may also be specified as an attribute of the ``<item>``
element, but specifying it as a child element of ``<item>`` is more flexible:
you can include newlines within an element, but not within an attribute.

.. _param-valid:

valid
^^^^^

Passed to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``valid`` argument. Must be ``True`` or ``False`` (the default).

In the XML file, ``valid`` is an attribute on the ``<item>`` element and must
have the value of either ``YES`` or ``NO``:

.. code-block:: xml
    :linenos:

    <item valid="YES">
        ...
    </item>
    <item valid="NO">
        ...
    </item>

``valid`` determines whether a user can hit ``ENTER`` on a result in Alfred's
results list or not (``"YES"``/``True`` meaning they can).

Specifying ``valid=True``/``valid="YES"`` has no effect if :ref:`arg <param-arg>`
isn't set.

.. _param-uid:

uid
^^^

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``uid`` argument. Must be :class:`unicode`.

Alfred uses the ``uid`` to uniquely identify a result and apply its "knowledge"
to it. That is to say, if (and only if) a user hits ``ENTER`` on a result with
a ``uid``, Alfred will associate that result (well, its ``uid``) with its
current query and prioritise that result for the same query in the future.

As a result, in most situations you should ensure that a particular item always
has the same ``uid``. In practice, setting ``uid`` to the same value as ``arg``
is a good choice.

If you omit ``uid``'s, Alfred will show results in the order in which they
appear in the XML file (the order in which you add them with
:meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>`).

.. _param-type:

type
^^^^

The type of the result. Currently, only ``"file"`` is supported.

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``type`` argument. Must be :class:`unicode`. Currently, the only allowed
value is ``"file"``.

If the ``type`` of a result is set to ``"file"`` (the only value currently
supported by Alfred), it will enable users to "action" the item, as in Alfred's
file browser, and show Alfred's File Actions (``Open``, ``Open with…``,
``Reveal in Finder`` etc.) using the default keyboard shortcut set in
``Alfred Preferences > File Search > Actions > Show Actions``.

For File Actions to work, :ref:`arg <param-arg>` must be set to a valid filepath,
but it is not necessary for the item to be :ref:`valid <param-valid>`.

.. _param-copytext:

copy text
^^^^^^^^^

Text that will be copied to the pasteboard if a user presses ``⌘+C`` on a
result.

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``copytext`` argument. Must be :class:`unicode`.

Set using ``<text type="copy">Copy text goes here</text>`` in XML.

If ``copytext`` is set, when the user presses ``⌘+C``, this will be copied to
the pasteboard and Alfred's window will close. If ``copytext`` is not set, the
selected result's :ref:`arg <param-arg>` value will be copied to the pasteboard
and Alfred's window will close. If neither is set, nothing will be copied to
the pasteboard and Alfred's window will close.

.. _param-largetext:

large text
^^^^^^^^^^

Text that will be displayed in Alfred's Large Type pop-up if a user presses
``⌘+L`` on a result.

Pass to :meth:`Workflow.add_item() <workflow.workflow.Workflow.add_item>` as
the ``largetext`` argument. Must be :class:`unicode`.

Set using ``<text type="largetype">Large text goes here</text>`` in XML.

If ``largetext`` is not set, when the user presses ``⌘+L`` on a result, Alfred
will display the current query in its Large Type pop-up.

.. _param-icon:

icon
^^^^