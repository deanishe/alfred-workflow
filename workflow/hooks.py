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

workflow_init = signal('workflow_init')
pre_run = signal('pre_run')
post_run = signal('post_run')
xml_generator_done = signal('xml_generator_done')
get_serializer = signal('get_serializer')
get_updater = signal('get_updater')
get_magic = signal('get_magic')
