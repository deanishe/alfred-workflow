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

from workflow import hooks


def test_hash_id():
    """Hashing is consistent"""
    def test1():
        pass

    def test2():
        pass

    # Functions
    h1 = hooks.hashable_identity(test1)
    h2 = hooks.hashable_identity(test1)
    h3 = hooks.hashable_identity(test2)
    assert h1 == h2
    assert h1 != h3
    # Methods
    h1 = hooks.hashable_identity(hooks.Signal.connect)
    h2 = hooks.hashable_identity(hooks.Signal.connect)
    h3 = hooks.hashable_identity(hooks.Signal.disconnect)
    assert h1 == h2
    assert h1 != h3
    # String objects
    assert hooks.hashable_identity('some text') == \
        hooks.hashable_identity('some text')
    assert hooks.hashable_identity('some text') == \
        hooks.hashable_identity(b'some text')


def test_signal_singletons():
    """Same name returns the same Signal instance"""
    name = 'my test'
    h1 = hooks.signal(name)
    h2 = hooks.signal(name)
    assert h1 is h2


def test_init():
    """Object created as expected"""
    name = 'test'
    doc = 'I am a test signal'
    s = hooks.Signal(name, doc)
    assert s.name == name
    assert s.__doc__ == doc
    assert s.receivers == []
    print(s)


def test_connect_disconnect():
    """Connect, receive, disconnect"""
    output = {}
    name = 'test'

    def cb(sender):
        output['result'] = sender

    # Connect
    s = hooks.signal(name)
    s.connect(cb)
    assert cb in s.receivers

    # Message received
    s.send('Test 1')
    assert output['result'] == 'Test 1'

    # Disconnect
    s.disconnect(cb)
    assert cb not in s.receivers

    # Message not received
    s.send('Test 2')
    assert output['result'] == 'Test 1'

    # Tidy up
    s.clear()
    assert s.receivers == []


def test_dead_receivers():
    """Dead receivers removed"""
    output = []

    def cb1(sender):
        output.append(sender)

    def cb2(sender):
        output.append(sender)

    s = hooks.signal('test')
    s.connect(cb1)
    s.connect(cb2)
    assert len(output) == 0

    s.send('Test 1')
    assert len(output) == 2

    del cb2
    s.send('Test 2')
    assert len(output) == 3


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
