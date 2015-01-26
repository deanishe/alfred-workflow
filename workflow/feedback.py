#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-26
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

try:
    import xml.etree.cElementTree as ET
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as ET


class Item(object):
    """Represents a feedback item for Alfred. Generates Alfred-compliant
    XML for a single item.

    You probably shouldn't use this class directly, but via
    :meth:`Workflow.add_item`. See :meth:`~Workflow.add_item`
    for details of arguments.

    """

    def __init__(self, title, subtitle=None, modifier_subtitles=None,
                 arg=None, autocomplete=None, valid=False, uid=None,
                 icon=None, icontype=None, type=None, largetext=None,
                 copytext=None):
        """Arguments the same as for :meth:`Workflow.add_item`.

        """

        self.title = title
        self.subtitle = subtitle
        self.modifier_subtitles = modifier_subtitles or {}
        self.arg = arg
        self.autocomplete = autocomplete
        self.valid = valid
        self.uid = uid
        self.icon = icon
        self.icontype = icontype
        self.type = type
        self.largetext = largetext
        self.copytext = copytext

    @property
    def elem(self):
        """Create and return feedback item for Alfred.

        :returns: :class:`Element <xml.etree.ElementTree.Element>`
            instance for this :class:`Item` instance.

        """

        # Attributes on <item> element
        attr = {}
        if self.valid:
            attr['valid'] = 'yes'
        else:
            attr['valid'] = 'no'
        # Allow empty string for autocomplete. This is a useful value,
        # as TABing the result will revert the query back to just the
        # keyword
        if self.autocomplete is not None:
            attr['autocomplete'] = self.autocomplete

        # Optional attributes
        for name in ('uid', 'type'):
            value = getattr(self, name, None)
            if value:
                attr[name] = value

        root = ET.Element('item', attr)
        ET.SubElement(root, 'title').text = self.title
        if self.subtitle is not None:
            ET.SubElement(root, 'subtitle').text = self.subtitle

        # Add modifier subtitles
        for mod in ('cmd', 'ctrl', 'alt', 'shift', 'fn'):
            if mod in self.modifier_subtitles:
                ET.SubElement(root, 'subtitle',
                              {'mod': mod}).text = self.modifier_subtitles[mod]

        # Add arg as element instead of attribute on <item>, as it's more
        # flexible (newlines aren't allowed in attributes)
        if self.arg:
            ET.SubElement(root, 'arg').text = self.arg

        # Add icon if there is one
        if self.icon:
            if self.icontype:
                attr = {'type': self.icontype}
            else:
                attr = {}
            ET.SubElement(root, 'icon', attr).text = self.icon

        if self.largetext:
            ET.SubElement(root, 'text',
                          {'type': 'largetype'}).text = self.largetext

        if self.copytext:
            ET.SubElement(root, 'text',
                          {'type': 'copy'}).text = self.copytext

        return root


class XMLGenerator(object):
    """Generates XML feedback for Alfred"""

    item_class = Item

    def __init__(self):
        self.items = []

    def add_item(self, title, subtitle=None, modifier_subtitles=None, arg=None,
                 autocomplete=None, valid=False, uid=None, icon=None,
                 icontype=None, type=None, largetext=None, copytext=None):
        """Add an item to be output to Alfred

        :param title: Title shown in Alfred
        :type title: ``unicode``
        :param subtitle: Subtitle shown in Alfred
        :type subtitle: ``unicode``
        :param modifier_subtitles: Subtitles shown when modifier
            (CMD, OPT etc.) is pressed. Use a ``dict`` with the lowercase
            keys ``cmd``, ``ctrl``, ``shift``, ``alt`` and ``fn``
        :type modifier_subtitles: ``dict``
        :param arg: Argument passed by Alfred as ``{query}`` when item is
            actioned
        :type arg: ``unicode``
        :param autocomplete: Text expanded in Alfred when item is TABbed
        :type autocomplete: ``unicode``
        :param valid: Whether or not item can be actioned
        :type valid: ``Boolean``
        :param uid: Used by Alfred to remember/sort items
        :type uid: ``unicode``
        :param icon: Filename of icon to use
        :type icon: ``unicode``
        :param icontype: Type of icon. Must be one of ``None`` , ``'filetype'``
           or ``'fileicon'``. Use ``'filetype'`` when ``icon`` is a filetype
           such as ``'public.folder'``. Use ``'fileicon'`` when you wish to
           use the icon of the file specified as ``icon``, e.g.
           ``icon='/Applications/Safari.app', icontype='fileicon'``.
           Leave as `None` if ``icon`` points to an actual
           icon file.
        :type icontype: ``unicode``
        :param type: Result type. Currently only ``'file'`` is supported
            (by Alfred). This will tell Alfred to enable file actions for
            this item.
        :type type: ``unicode``
        :param largetext: Text to be displayed in Alfred's large text box
            if user presses CMD+L on item.
        :type largetext: ``unicode``
        :param copytext: Text to be copied to pasteboard if user presses
            CMD+C on item.
        :type copytext: ``unicode``
        :returns: :class:`Item` instance

        See the :ref:`script-filter-results` section of the documentation
        for a detailed description of what the various parameters do and how
        they interact with one another.

        See :ref:`icons` for a list of the supported system icons.

        .. note::

            Although this method returns an :class:`Item` instance, you don't
            need to hold onto it or worry about it. All generated :class:`Item`
            instances are also collected internally and sent to Alfred when
            :meth:`send_feedback` is called.

            The generated :class:`Item` is only returned in case you want to
            edit it or do something with it other than send it to Alfred.

        """

        item = self.item_class(title, subtitle, modifier_subtitles, arg,
                               autocomplete, valid, uid, icon, icontype, type,
                               largetext, copytext)
        self.items.append(item)
        return item

    def __str__(self):
        """Synonym for :meth:`xml`"""
        return self.xml()

    def xml(self, encoding='utf-8'):
        """Generate and return XML

        Returns XML as bytestring encoded with ``encoding``.

        """

        output = ['<?xml version="1.0" encoding="{0}"?>'.format(encoding)]
        root = ET.Element('items')
        for item in self.items:
            root.append(item.elem)
        output.append(ET.tostring(root).encode(encoding))
        return ''.join(output)
