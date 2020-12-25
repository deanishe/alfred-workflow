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



import json
import os
from io import StringIO
import sys

import pytest

from workflow import ICON_WARNING, Variables, Workflow3

from .test_util import MockCall
from .conftest import env


def test_required_optional(infopl):
    """Item3: Required and optional values."""
    wf = Workflow3()
    it = wf.add_item('Title')
    assert it.title == 'Title'
    o = it.obj
    assert o['title'] == 'Title'
    assert o['valid'] is False
    assert o['subtitle'] == ''
    assert set(o.keys()) == {'title', 'valid', 'subtitle'}


def test_optional(infopl):
    """Item3: Optional values."""
    wf = Workflow3()
    it = wf.add_item('Title', 'Subtitle',
                     arg='argument',
                     uid='uid',
                     valid=True,
                     autocomplete='auto',
                     match='match',
                     largetext='large',
                     copytext='copy',
                     quicklookurl='http://www.deanishe.net/alfred-workflow',
                     type='file',
                     icon='icon.png')

    o = it.obj
    assert o['title'] == 'Title'
    assert o['valid'] is True
    assert o['autocomplete'] == 'auto'
    assert o['match'] == 'match'
    assert o['uid'] == 'uid'
    assert o['text']['copy'] == 'copy'
    assert o['text']['largetype'] == 'large'
    assert o['icon']['path'] == 'icon.png'
    assert o['quicklookurl'] == 'http://www.deanishe.net/alfred-workflow'
    assert o['type'] == 'file'


def test_icontype(infopl):
    """Item3: Icon type."""
    wf = Workflow3()
    it = wf.add_item('Title', icon='icon.png', icontype='filetype')
    o = it.obj
    assert o['icon']['path'] == 'icon.png'
    assert o['icon']['type'] == 'filetype'


def test_feedback(infopl):
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


def test_warn_empty(infopl):
    """Workflow3: Warn empty."""
    wf = Workflow3()
    it = wf.warn_empty('My warning')

    assert it.title == 'My warning'
    assert it.subtitle == ''
    assert it.valid is False
    assert it.icon == ICON_WARNING

    o = wf.obj

    assert len(o['items']) == 1
    assert o['items'][0] == it.obj

    # Non-empty feedback
    wf = Workflow3()
    wf.add_item('Real item')
    it = wf.warn_empty('Warning')

    assert it is None

    o = wf.obj

    assert len(o['items']) == 1


def test_arg_multiple(infopl):
    """Item3: multiple args."""
    wf = Workflow3()
    arg = ['one', 'two']
    it = wf.add_item('Title', arg=arg)

    o = it.obj
    assert o['arg'] == arg

    o = wf.obj
    assert len(o['items']) == 1
    o = o['items'][0]
    assert o['arg'] == arg


def test_arg_variables(infopl):
    """Item3: Variables in arg."""
    wf = Workflow3()
    it = wf.add_item('Title')
    it.setvar('key1', 'value1')
    o = it.obj
    assert 'variables' in o
    assert 'config' not in o
    assert o['variables']['key1'] == 'value1'


def test_feedback_variables(infopl):
    """Workflow3: feedback variables."""
    wf = Workflow3()

    o = wf.obj
    assert 'variables' not in o

    wf.setvar('prevar', 'preval')
    it = wf.add_item('Title', arg='something')
    wf.setvar('postvar', 'postval')

    assert wf.getvar('prevar') == 'preval'
    assert wf.getvar('postvar') == 'postval'
    assert it.getvar('prevar') == 'preval'
    assert it.getvar('postvar') is None

    o = wf.obj
    assert 'variables' in o
    assert o['variables']['prevar'] == 'preval'
    assert o['variables']['postvar'] == 'postval'

    o = it.obj
    assert 'variables' in o
    assert o['variables']['prevar'] == 'preval'
    assert 'postval' not in o['variables']


def test_persistent_variables3(alfred3):
    """Persistent variables Alfred 3"""
    _test_persistent_variables('Alfred 3')


def test_persistent_variables(alfred4):
    """Persistent variables Alfred 4+"""
    _test_persistent_variables('com.runningwithcrayons.Alfred')


def _test_persistent_variables(appname):
    wf = Workflow3()
    o = wf.obj
    assert 'variables' not in o

    name = 'testvar'
    value = 'testval'

    # Without persistence
    with MockCall() as m:
        wf.setvar(name, value)
        assert m.cmd is None

    # With persistence
        script = (
            'Application("' + appname + '")'
            '.setConfiguration("testvar", '
            '{"exportable": false, '
            '"inWorkflow": "net.deanishe.alfred-workflow", '
            '"toValue": "testval"});'
        )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        wf.setvar(name, value, True)
        assert m.cmd == cmd


def test_rerun(infopl):
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


def test_session_id(infopl):
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

    # load from environment variable
    sid = 'thisisatest'
    with env(_WF_SESSION_ID=sid):
        wf = Workflow3()
        o = wf.obj
        assert 'variables' in o
        assert '_WF_SESSION_ID' in o['variables']
        assert o['variables']['_WF_SESSION_ID'] == sid
        assert wf.session_id == sid


def test_session_cache(infopl):
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


def test_clear_session_cache(infopl):
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

    # current session files kept
    assert len(_sessfiles()) == 1
    assert len(os.listdir(wf.cachedir)) > 0
    assert wf.cached_data('data', session=True) == data
    assert wf.cached_data('data', session=False) == data

    # also clear data for current session
    wf.clear_session_cache(True)

    # sessions files are gone, but other cache files are not
    assert len(_sessfiles()) == 0
    assert len(os.listdir(wf.cachedir)) > 0
    assert wf.cached_data('data', session=True) is None
    assert wf.cached_data('data', session=False) == data


def test_modifiers(infopl):
    """Item3: Modifiers."""
    wf = Workflow3()
    wf.setvar('wfprevar', 'wfpreval')

    it = wf.add_item('Title', 'Subtitle', arg='value', valid=False)
    it.setvar('prevar', 'preval')
    mod = it.add_modifier('cmd', subtitle='Subtitle2',
                          arg='value2', valid=True)
    it.setvar('postvar', 'postval')
    wf.setvar('wfpostvar', 'wfpostval')
    mod.setvar('modvar', 'hello')

    # assert wf.getvar('prevar') == 'preval'
    # Test variable inheritance
    assert it.getvar('prevar') == 'preval'
    assert mod.getvar('prevar') == 'preval'
    assert it.getvar('postvar') == 'postval'
    assert mod.getvar('postvar') is None

    assert it.getvar('wfprevar') == 'wfpreval'
    assert mod.getvar('wfprevar') == 'wfpreval'
    assert it.getvar('wfpostvar') is None
    assert mod.getvar('wfpostvar') is None

    o = it.obj
    assert 'mods' in o
    assert set(o['mods'].keys()) == {'cmd'}

    m = o['mods']['cmd']
    assert m['valid'] is True
    assert m['subtitle'] == 'Subtitle2'

    assert m['arg'] == 'value2'
    assert m['variables']['prevar'] == 'preval'
    assert m['variables']['modvar'] == 'hello'


def test_modifier_multiple_args(infopl):
    """Item3: Modifier multiple args."""
    wf = Workflow3()
    arg = ['one', 'two']
    marg = ['three', 'four']
    it = wf.add_item('Title', arg=arg)
    mod = it.add_modifier('cmd', arg=marg)

    o = it.obj
    assert o['arg'] == arg

    assert o['mods']['cmd']['arg'] == marg

    assert mod.arg == marg
    assert mod.obj['arg'] == marg


def test_modifier_icon(infopl):
    """Item3: Modifier icon."""
    wf = Workflow3()
    it = wf.add_item('Title', 'Subtitle')
    mod = it.add_modifier('cmd', subtitle='Subtitle2',
                          icon='icon.png')
    o = mod.obj
    assert 'icon' in o
    assert o['icon'] == {'path': 'icon.png'}

    mod = it.add_modifier('cmd', subtitle='Subtitle2',
                          icon='/Applications/Safari.app',
                          icontype='fileicon')
    o = mod.obj
    assert 'icon' in o
    assert o['icon'] == {
        'path': '/Applications/Safari.app',
        'type': 'fileicon',
    }


def test_item_config(infopl):
    """Item3: Config."""
    wf = Workflow3()
    it = wf.add_item('Title')
    it.config['var1'] = 'val1'

    m = it.add_modifier('cmd')
    m.config['var1'] = 'val2'

    o = it.obj

    assert 'config' in o
    assert set(o['config'].keys()) == {'var1'}
    assert o['config']['var1'] == 'val1'

    assert 'mods' in o
    assert 'cmd' in o['mods']
    assert 'config' in o['mods']['cmd']

    o2 = m.obj
    c = o2['config']
    assert c['var1'] == 'val2'


def _test_default_directories(data, cache):
    wf3 = Workflow3()
    assert wf3.datadir.startswith(data), "unexpected data directory"
    assert wf3.cachedir.startswith(cache), "unexpected cache directory"


def test_default_directories3(alfred3):
    """Default directories (Alfred 3)"""
    from os.path import expanduser
    _test_default_directories(
        expanduser('~/Library/Application Support/Alfred 3/Workflow Data/'),
        expanduser('~/Library/Caches/com.runningwithcrayons.Alfred-3/'
                   'Workflow Data/'))


def test_default_directories(alfred4):
    """Default directories (Alfred 4+)"""
    from os.path import expanduser
    _test_default_directories(
        expanduser('~/Library/Application Support/Alfred/Workflow Data/'),
        expanduser('~/Library/Caches/com.runningwithcrayons.Alfred/'
                   'Workflow Data/'))

    with env(alfred_workflow_data=None, alfred_workflow_cache=None):
        _test_default_directories(
            expanduser('~/Library/Application Support/Alfred/'
                       'Workflow Data/'),
            expanduser('~/Library/Caches/com.runningwithcrayons.Alfred/'
                       'Workflow Data/'))


def test_run_fails_with_json_output(infopl):
    """Run fails with JSON output"""
    error_text = 'Have an error'

    def cb(wf):
        raise ValueError(error_text)

    # named after bundleid
    wf = Workflow3()
    wf.bundleid

    stdout = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    ret = wf.run(cb)
    sys.stdout = stdout
    output = buf.getvalue()
    buf.close()

    assert ret == 1
    assert error_text in output
    assert '{' in output


def test_run_fails_with_plain_text_output(infopl):
    """Run fails with plain text output"""
    error_text = 'Have an error'

    def cb(wf):
        raise ValueError(error_text)

    # named after bundleid
    wf = Workflow3()
    wf.bundleid

    stdout = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    ret = wf.run(cb, text_errors=True)
    sys.stdout = stdout
    output = buf.getvalue()
    buf.close()

    assert ret == 1
    assert error_text in output
    assert '{' not in output


def test_variables_plain_arg():
    """Arg-only returns string, not JSON."""
    v = Variables(arg='test')
    assert str(v) == 'test'
    assert str(v) == 'test'


def test_variables_multiple_args(infopl):
    """Variables: multiple args."""
    arg = ['one', 'two']
    js = '{"alfredworkflow": {"arg": ["one", "two"]}}'
    v = Variables(arg=arg)
    assert v.obj == {'alfredworkflow': {'arg': arg}}
    assert str(v) == js
    assert str(v) == js


def test_variables_empty():
    """Empty Variables returns empty string."""
    v = Variables()
    assert str(v) == ''
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
    v = Variables(arg='fübar', englisch='englisch')
    v['französisch'] = 'französisch'
    v.config['über'] = 'über'
    d = {
        'alfredworkflow':
            {
                'arg': 'fübar',
                'variables': {
                    'englisch': 'englisch',
                    'französisch': 'französisch',
                },
                'config': {'über': 'über'}
            }
    }
    print((repr(v.obj)))
    print((repr(d)))
    assert v.obj == d

    # Round-trip to JSON and back
    d2 = json.loads(str(v))
    assert d2 == d


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
