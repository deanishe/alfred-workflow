# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-06-25
#

"""
:class:`Workflow3` is an Alfred 3-only version of
:class:`~workflow.workflow.Workflow`.

It supports setting :ref:`workflow-variables` and
:class:`the more advanced modifiers <Modifier>` supported by Alfred 3.

In order for the feedback mechanism to work correctly, it's important
to create :class:`Item3` and :class:`Modifier` objects via the
:meth:`Workflow3.add_item()` and :meth:`Item3.add_modifier()` methods
respectively.
"""

from __future__ import print_function, unicode_literals, absolute_import

import json
import sys

from .workflow import Workflow


class Modifier(object):
    """Modify ``Item3`` values for when specified modifier keys are pressed.

    Valid modifiers (i.e. values for ``key``) are:

     * cmd
     * alt
     * shift
     * ctrl
     * fn

    Attributes:
        arg (unicode): Arg to pass to following action.
        key (unicode): Modifier key (see above).
        subtitle (unicode): Override item subtitle.
        valid (bool): Override item validity.
        variables (dict): Workflow variables set by this modifier.

    """

    def __init__(self, key, subtitle=None, arg=None, valid=None):
        """Create a new :class:`Modifier`.

        You probably don't want to use this class directly, but rather
        use :meth:`Item3.add_modifier()` to add modifiers to results.

        Args:
            key (unicode): Modifier key, e.g. ``"cmd"``, ``"alt"`` etc.
            subtitle (unicode, optional): Override default subtitle.
            arg (unicode, optional): Argument to pass for this modifier.
            valid (bool, optional): Override item's validity.
        """
        self.key = key
        self.subtitle = subtitle
        self.arg = arg
        self.valid = valid

        self.config = {}
        self.variables = {}

    def setvar(self, name, value):
        """Set a workflow variable for this Item.

        Args:
            name (unicode): Name of variable.
            value (unicode): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name, default=None):
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (unicode): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            unicode or ``default``: Value of variable if set or ``default``.
        """
        return self.variables.get(name, default)

    @property
    def obj(self):
        """Return modifier for Alfred 3 feedback JSON.

        Returns:
            dict: Modifier for serializing to JSON.
        """
        o = {}

        if self.subtitle is not None:
            o['subtitle'] = self.subtitle

        if self.arg is not None:
            o['arg'] = self.arg

        if self.valid is not None:
            o['valid'] = self.valid

        # Variables and config
        if self.variables or self.config:
            d = {}
            if self.variables:
                d['variables'] = self.variables

            if self.config:
                d['config'] = self.config

            if self.arg is not None:
                d['arg'] = self.arg

            o['arg'] = json.dumps({'alfredworkflow': d})

        return o


class Item3(object):
    """Represents a feedback item for Alfred 3.

    Generates Alfred-compliant XML for a single item.

    You probably shouldn't use this class directly, but via
    :meth:`Workflow3.add_item`. See :meth:`~Workflow3.add_item`
    for details of arguments.

    """

    def __init__(self, title, subtitle='', arg=None, autocomplete=None,
                 valid=False, uid=None, icon=None, icontype=None,
                 type=None, largetext=None, copytext=None):
        """Use same arguments as for :meth:`Workflow.add_item`.

        Argument ``subtitle_modifiers`` is not supported.

        """

        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.autocomplete = autocomplete
        self.valid = valid
        self.uid = uid
        self.icon = icon
        self.icontype = icontype
        self.type = type
        self.largetext = largetext
        self.copytext = copytext

        self.modifiers = {}

        self.config = {}
        self.variables = {}

    def setvar(self, name, value):
        """Set a workflow variable for this Item.

        Args:
            name (unicode): Name of variable.
            value (unicode): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name, default=None):
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (unicode): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            unicode or ``default``: Value of variable if set or ``default``.
        """
        return self.variables.get(name, default)

    def add_modifier(self, key, subtitle=None, arg=None, valid=None):
        """Add alternative values for a modifier key.

        Args:
            key (unicode): Modifier key, e.g. ``"cmd"`` or ``"alt"``
            subtitle (unicode, optional): Override item subtitle.
            arg (unicode, optional): Input for following action.
            valid (bool, optional): Override item validity.

        Returns:
            Modifier: Configured :class:`Modifier`.
        """
        mod = Modifier(key, subtitle, arg, valid)

        for k in self.variables:
            mod.setvar(k, self.variables[k])

        self.modifiers[key] = mod

        return mod

    @property
    def obj(self):
        """Return Modifier formatted for JSON serialization.

        Returns:
            dict: Data suitable for Alfred 3 feedback.
        """
        o = {'title': self.title,
             'subtitle': self.subtitle,
             'valid': self.valid}

        text = {}
        icon = {}

        if self.arg is not None:
            o['arg'] = self.arg

        if self.autocomplete is not None:
            o['autocomplete'] = self.autocomplete

        if self.uid is not None:
            o['uid'] = self.uid

        if self.type is not None:
            o['type'] = self.type

        # Largetype and copytext
        if self.largetext is not None:
            text['largetype'] = self.largetext

        if self.copytext is not None:
            text['copy'] = self.copytext

        if text:
            o['text'] = text

        # Icon
        if self.icon is not None:
            icon['path'] = self.icon

        if self.icontype is not None:
            icon['type'] = self.icontype

        if icon:
            o['icon'] = icon

        # Variables and config
        if self.variables or self.config:
            d = {}
            if self.variables:
                d['variables'] = self.variables

            if self.config:
                d['config'] = self.config

            if self.arg is not None:
                d['arg'] = self.arg

            o['arg'] = json.dumps({'alfredworkflow': d})

        # Modifiers
        if self.modifiers:
            mods = {}
            for k, mod in self.modifiers.items():
                mods[k] = mod.obj

            o['mods'] = mods

        return o


class Workflow3(Workflow):
    """Workflow class that generates Alfred 3 feedback."""

    item_class = Item3

    def __init__(self, **kwargs):
        Workflow.__init__(self, **kwargs)
        self.variables = {}

    def setvar(self, name, value):
        """Set a workflow variable that will be inherited by all new items.

        Args:
            name (unicode): Name of variable.
            value (unicode): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name, default=None):
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (unicode): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            unicode or ``default``: Value of variable if set or ``default``.
        """
        return self.variables.get(name, default)

    def add_item(self, title, subtitle='', arg=None, autocomplete=None,
                 valid=False, uid=None, icon=None, icontype=None,
                 type=None, largetext=None, copytext=None):
        """Add an item to be output to Alfred.

        See :meth:`~workflow.workflow.Workflow.add_item` for the main
        documentation.

        The key difference is that this method does not support the
        ``modifier_subtitles`` argument. Use the :meth:`~Item3.add_modifier()`
        method instead on the returned item instead.

        Returns:
            Item3: Alfred feedback item.

        """
        item = self.item_class(title, subtitle, arg,
                               autocomplete, valid, uid, icon, icontype, type,
                               largetext, copytext)

        for k in self.variables:
            item.setvar(k, self.variables[k])

        self._items.append(item)
        return item

    def send_feedback(self):
        """Print stored items to console/Alfred as JSON."""
        items = []
        for item in self._items:
            items.append(item.obj)

        json.dump({'items': items}, sys.stdout)
        sys.stdout.flush()
