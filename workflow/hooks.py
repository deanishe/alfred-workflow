#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-24
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import weakref

from workflow import base

log = base.get_logger(__name__)


def hashable_identity(obj):
    if hasattr(obj, '__func__'):
        return (id(obj.__func__), id(obj.__self__))
    elif isinstance(obj, basestring):
        return obj
    else:
        return id(obj)


# def first_result(results):
#     """Get first non-``None`` receiver and result from a signal send.

#     :param results: list of ``(receiver, result)`` tuples
#     :returns: ``(receiver, result)`` tuple

#     If ``receiver`` is ``None``, there were no results.

#     """

#     for receiver, result in results:
#         if result is not None:
#             return (receiver, result)
#     return (None, None)


class Signal(object):
    """Simple signal emitter.
    """

    def __init__(self, name, doc=None):
        self.name = name
        if doc:
            self.__doc__ = doc

        self._receivers = {}

    def connect(self, receiver):
        """Add ``receiver`` as a subscriber to messages

        ``receiver`` will be called with ``sender`` and any keyword
        arguments passed to :meth:`send`.

        :param receiver: callable to be called when signal fires

        """
        id_ = hashable_identity(receiver)
        ref = weakref.ref(receiver)
        self._receivers[id_] = ref
        log.debug('[{0}] Connected new receiver {1}'.format(self.name, id_))
        del ref

    def disconnect(self, receiver):
        """Remove ``receiver`` from subscription list

        :param receiver: Object to remove from list of subscribers

        """

        id_ = hashable_identity(receiver)
        if id_ in self._receivers:
            del self._receivers[id_]
            log.debug('[{0}] Removed receiver {1}'.format(self.name, id_))

    def send(self, sender, **kwargs):
        """Emit this signal

        Call all :attr:`receivers` with ``sender`` and ``**kwargs``.
        Returns a list of 2-tuples of receiver object and the return value
        of the call to the receiver.

        :param sender: First argument to be passed to receivers
        :param **kwargs: Additional arguments to pass to receivers
        :returns: list of tuples ``(receiver, call results)`` for each
            receiver
        :rtype: list

        """

        log.debug('[{0}] Send {1!r}'.format(self.name, sender))
        if not self.receivers:
            return []
        return [(receiver, receiver(sender, **kwargs))
                for receiver in self.receivers]

    @property
    def receivers(self):
        """List of all active (undead) receivers"""

        result = []
        for id_ in self._receivers.keys():
            ref = self._receivers[id_]
            obj = ref()
            if obj is None:
                del self._receivers[id_]
                log.debug('[{0}] Removed dead receiver {1}'.format(self.name,
                                                                   id_))
            else:
                result.append(obj)
            del ref
        return result

    def first_response(self, sender, **kwargs):
        """Return receiver and first non-``None`` result of :meth:`send`.

        :returns: ``(receiver, result)`` tuple

        If ``receiver`` is ``None`` (i.e. ``(None, None)`` is returned),
        there were no results.

        Arguments passed through to :meth:`send`.

        """

        results = self.send(sender, **kwargs)

        for receiver, result in results:
            if result is not None:
                return (receiver, result)

        return (None, None)

    def clear(self):
        """Remove all receivers"""
        self._receivers.clear()

    def __repr__(self):
        return 'Signal({0!r})'.format(self.name)


class Namespace(dict):

    def signal(self, name, doc=None):
        try:
            return self[name]
        except KeyError:
            return self.setdefault(name, Signal(name, doc))


signal = Namespace().signal

#: Sent at the end of :meth:`Workflow.__init__ `workflow.workflow.Workflow>`.
#: ``sender`` is :class:`~workflow.workflow.Workflow` instance.
workflow_initialized = signal('workflow_initialized')
#: Sent before :meth:`Workflow.run <workflow.workflow.Workflow.run>`
#: runs your workflow's main function.
#: ``sender`` is :class:`~workflow.workflow.Workflow` instance.
workflow_will_run = signal('workflow_will_run')
#: Sent after :meth:`Workflow.run <workflow.workflow.Workflow.run>`
#: runs your workflow's main function.
#: ``sender`` is :class:`~workflow.workflow.Workflow` instance.
workflow_did_run = signal('workflow_did_run')
#: Sent after :meth:`Workflow.run <workflow.workflow.Workflow.run>`
#: catches an Exception and before it handles it. Access the
#: Exception at ``Workflow.exception``.
workflow_error = signal('workflow_error')
#: Sent when XML generation is complete.
#: ``sender`` is the XML bytestring, UTF-8 encoded by default.
#: Result should be XML bytestring or ``None``.
xml_generator_done = signal('xml_generator_done')
#: Sent when a serializer is required.
#: ``sender`` is the string format name, e.g. ``'json'`` or ``'pickle'``.
get_serializer = signal('get_serializer')
#: Sent when an updater is required.
#: ``sender`` is :class:`~workflow.update.UpdateManager` instance.
get_updater = signal('get_updater')
#: Sent when a magic arg has been found.
#: ``sender`` is unicode magic argument without the prefix.
#: The result should be a callable or ``None``.
get_magic = signal('get_magic')
