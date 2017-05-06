#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-06-25
#

"""Test Workflow3 feedback."""

from __future__ import print_function, absolute_import

import json
import os
from StringIO import StringIO
import sys

import pytest

from workflow.workflow3 import Variables, Workflow3


def test_required_optional(info3):
    """Item3: Required and optional values."""
    wf = Workflow3()
    it = wf.add_item('Title')
    assert it.title == 'Title'
    o = it.obj
    assert o['title'] == 'Title'
    assert o['valid'] is False
    assert o['subtitle'] == ''
    assert set(o.keys()) == set(['title', 'valid', 'subtitle'])


def test_optional(info3):
    """Item3: Optional values."""
    wf = Workflow3()
    it = wf.add_item('Title', 'Subtitle',
                     arg='argument',
                     uid='uid',
                     valid=True,
                     autocomplete='auto',
                     largetext='large',
                     copytext='copy',
                     quicklookurl='http://www.deanishe.net/alfred-workflow',
                     type='file',
                     icon='icon.png')

    o = it.obj
    assert o['title'] == 'Title'
    assert o['valid'] is True
    assert o['autocomplete'] == 'auto'
    assert o['uid'] == 'uid'
    assert o['text']['copy'] == 'copy'
    assert o['text']['largetype'] == 'large'
    assert o['icon']['path'] == 'icon.png'
    assert o['quicklookurl'] == 'http://www.deanishe.net/alfred-workflow'
    assert o['type'] == 'file'


def test_icontype(info3):
    """Item3: Icon type."""
    wf = Workflow3()
    it = wf.add_item('Title', icon='icon.png', icontype='filetype')
    o = it.obj
    assert o['icon']['path'] == 'icon.png'
    assert o['icon']['type'] == 'filetype'


def test_feedback(info3):
    """Workflow3: Feedback."""
    wf = Workflow3()
    for i in range(10):
        wf.add_item('Title {0:2d}'.format(i + 1))

    orig = sys.stdout
    stdout = StringIO()
    try:
        sys.stdout = stdout
        wf.send_feedback()
    finally:
        sys.stdout = orig

    s = stdout.getvalue()

    assert len(s) > 0

    o = json.loads(s)

    assert isinstance(o, dict)

    items = o['items']

    assert len(items) == 10
    for i in range(10):
        assert items[i]['title'] == 'Title {0:2d}'.format(i + 1)


def test_arg_variables(info3):
    """Item3: Variables in arg."""
    wf = Workflow3()
    it = wf.add_item('Title')
    it.setvar('key1', 'value1')
    o = it.obj
    o2 = json.loads(o['arg'])
    assert 'alfredworkflow' in o2
    r = o2['alfredworkflow']
    assert r['variables']['key1'] == 'value1'
    assert 'config' not in r


def test_feedback_variables(info3):
    """Workflow3: feedback variables."""
    wf = Workflow3()

    o = wf.obj
    assert 'variables' not in o

    wf.setvar('var', 'val')
    it = wf.add_item('Title', arg='something')

    assert wf.getvar('var') == 'val'
    assert it.getvar('var') is None

    o = wf.obj
    assert 'variables' in o
    assert o['variables']['var'] == 'val'


def test_rerun(info3):
    """Workflow3: rerun."""
    wf = Workflow3()
    o = wf.obj
    assert 'rerun' not in o
    assert wf.rerun == 0

    wf.rerun = 1

    o = wf.obj
    assert 'rerun' in o
    assert o['rerun'] == 1
    assert wf.rerun == 1


def test_session_id(info3):
    """Workflow3: session_id."""
    wf = Workflow3()
    o = wf.obj
    assert 'variables' not in o

    sid = wf.session_id
    assert sid

    o = wf.obj
    assert 'variables' in o
    assert '_WF_SESSION_ID' in o['variables']
    assert o['variables']['_WF_SESSION_ID'] == sid

    sid = 'thisisatest'
    os.environ['_WF_SESSION_ID'] = sid
    wf = Workflow3()
    try:
        assert wf.session_id == sid
    finally:
        del os.environ['_WF_SESSION_ID']


def test_session_cache(info3):
    """Workflow3: session-scoped caching."""
    wf1 = Workflow3()
    wf2 = Workflow3()
    data1 = {'foo': 'bar'}
    data2 = {'bar': 'foo'}
    # sid = wf.session_id
    wf1.cache_data('data', data1, session=True)
    wf2.cache_data('data', data2, session=True)
    assert wf1.cached_data('data', session=True) == data1
    assert wf2.cached_data('data', session=True) == data2


def test_clear_session_cache(info3):
    """Workflow3: session-scoped caching."""
    wf = Workflow3()
    data = {'foo': 'bar'}
    wf.clear_cache()

    assert len(os.listdir(wf.cachedir)) == 0

    # save session and non-session data
    wf.cache_data('data', data, session=True)
    wf.cache_data('data', data, session=False)

    def _sessfiles():
        return [n for n in os.listdir(wf.cachedir)
                if n.startswith('_wfsess-')]

    assert len(_sessfiles()) > 0

    wf.clear_session_cache()

    # sessions files are gone, but other cache files are not
    assert len(_sessfiles()) == 0
    assert len(os.listdir(wf.cachedir)) > 0
    assert wf.cached_data('data', session=True) is None
    assert wf.cached_data('data', session=False) == data


def test_modifiers(info3):
    """Item3: Modifiers."""
    wf = Workflow3()
    it = wf.add_item('Title', 'Subtitle', arg='value', valid=False)
    it.setvar('prevar', 'preval')
    mod = it.add_modifier('cmd', subtitle='Subtitle2',
                          arg='value2', valid=True)
    it.setvar('postvar', 'postval')
    mod.setvar('modvar', 'hello')

    # assert wf.getvar('prevar') == 'preval'
    # Test variable inheritance
    assert it.getvar('prevar') == 'preval'
    assert mod.getvar('prevar') == 'preval'
    assert it.getvar('postvar') == 'postval'
    assert mod.getvar('postvar') is None

    o = it.obj
    assert 'mods' in o
    assert set(o['mods'].keys()) == set(['cmd'])

    m = o['mods']['cmd']
    assert m['valid'] is True
    assert m['subtitle'] == 'Subtitle2'

    r = json.loads(m['arg'])['alfredworkflow']
    assert r['arg'] == 'value2'
    assert r['variables']['prevar'] == 'preval'
    assert r['variables']['modvar'] == 'hello'


def test_item_config(info3):
    """Item3: Config."""
    wf = Workflow3()
    it = wf.add_item('Title')
    it.config['var1'] = 'val1'

    m = it.add_modifier('cmd')
    m.config['var1'] = 'val2'

    o = it.obj
    r = json.loads(o['arg'])['alfredworkflow']

    assert 'config' in r
    assert set(r['config'].keys()) == set(['var1'])
    assert r['config']['var1'] == 'val1'

    assert 'mods' in o
    assert 'cmd' in o['mods']
    r = json.loads(o['mods']['cmd']['arg'])['alfredworkflow']
    assert 'config' in r

    c = r['config']
    assert c['var1'] == 'val2'


def test_default_directories(info3):
    """Workflow3: Default directories."""
    wf3 = Workflow3()
    assert 'Alfred 3' in wf3.datadir
    assert 'Alfred-3' in wf3.cachedir


def test_run_fails_with_json_output():
    """Run fails with JSON output"""
    error_text = 'Have an error'

    def cb(wf):
        raise ValueError(error_text)

    # named after bundleid
    wf = Workflow3()
    wf.bundleid

    stdout = sys.stdout
    sio = StringIO()
    sys.stdout = sio
    ret = wf.run(cb)
    sys.stdout = stdout
    output = sio.getvalue()
    sio.close()

    assert ret == 1
    assert error_text in output
    assert '{' in output


def test_run_fails_with_plain_text_output():
    """Run fails with plain text output"""
    error_text = 'Have an error'

    def cb(wf):
        raise ValueError(error_text)

    # named after bundleid
    wf = Workflow3()
    wf.bundleid

    stdout = sys.stdout
    sio = StringIO()
    sys.stdout = sio
    ret = wf.run(cb, text_errors=True)
    sys.stdout = stdout
    output = sio.getvalue()
    sio.close()

    assert ret == 1
    assert error_text in output
    assert '{' not in output


def test_variables_plain_arg():
    """Arg-only returns string, not JSON."""
    v = Variables(arg=u'test')
    assert unicode(v) == u'test'
    assert str(v) == 'test'


def test_variables_empty():
    """Empty Variables returns empty string."""
    v = Variables()
    assert unicode(v) == u''
    assert str(v) == ''


def test_variables():
    """Set variables correctly."""
    v = Variables(a=1, b=2)
    assert v.obj == {'alfredworkflow': {'variables': {'a': 1, 'b': 2}}}


def test_variables_config():
    """Set config correctly."""
    v = Variables()
    v.config['var'] = 'val'
    assert v.obj == {'alfredworkflow': {'config': {'var': 'val'}}}


def test_variables_unicode():
    """Unicode handled correctly."""
    v = Variables(arg=u'fübar', englisch='englisch')
    v[u'französisch'] = u'französisch'
    v.config[u'über'] = u'über'
    assert v.obj == {
        'alfredworkflow':
            {
                'arg': u'fübar',
                'variables': {
                    'englisch': u'englisch',
                    u'französisch': u'französisch',
                },
                'config': {u'über': u'über'}
            }
    }


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
