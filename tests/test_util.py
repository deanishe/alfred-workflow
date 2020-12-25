#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-17
#

"""Unit tests for workflow/util.py."""



import os
import shutil
import subprocess
import tempfile

import pytest

from .conftest import env
from workflow.util import (
    action_in_alfred,
    appinfo,
    applescriptify,
    browse_in_alfred,
    jxa_app_name,
    reload_workflow,
    run_applescript,
    run_command,
    run_jxa,
    run_trigger,
    search_in_alfred,
    set_config,
    set_theme,
    unicodify,
    unset_config,
    utf8ify,
)

from .util import MockCall


@pytest.fixture(scope='function')
def testfile(request):
    """Test filepath."""
    tempdir = tempfile.mkdtemp()
    testfile = os.path.join(tempdir, 'testfile')

    def rm():
        shutil.rmtree(tempdir)

    request.addfinalizer(rm)

    return testfile

@pytest.mark.xfail(reason='unnecessary in python3')
def test_unicodify():
    """Unicode decoding."""
    data = [
        # input, normalisation form, expected output
        ('Köln', None, 'Köln'),
        ('Köln', None, 'Köln'),
        ('Köln', 'NFC', 'K\xf6ln'),
        ('Köln', 'NFD', 'Ko\\u0308ln'),
        ('UTF-8', None, 'UTF-8'),
    ]

    for b, n, x in data:
        s = unicodify(b, norm=n)
        assert s == x
        assert isinstance(s, str)


def test_utf8ify():
    """UTF-8 encoding."""
    data = [
        # input, expected output
        ('Köln', 'Köln'),
        ('UTF-8', 'UTF-8'),
        (10, '10'),
        ([1, 2, 3], '[1, 2, 3]'),
    ]

    for s, x in data:
        r = utf8ify(s)
        assert x == r
        assert isinstance(x, str)


def test_applescript_escape():
    """Escape AppleScript strings."""
    data = [
        # input, expected output
        ('no change', 'no change'),
        ('has "quotes" in it', 'has " & quote & "quotes" & quote & " in it'),
    ]

    for s, x in data:
        r = applescriptify(s)
        assert x == r
        assert isinstance(x, str)


def test_run_command():
    """Run command."""
    data = [
        # command, expected output
        (['echo', '-n', 1], '1'),
        (['echo', '-n', 'Köln'], 'Köln'),
    ]

    for cmd, x in data:
        r = run_command(cmd)
        assert r == x

    with pytest.raises(subprocess.CalledProcessError):
        run_command(['/usr/bin/false'])


def test_run_applescript(testfile):
    """Run AppleScript."""
    # Run script passed as text
    out = run_applescript('return "1"')
    assert out.strip() == '1'

    # Run script file
    with open(testfile, 'w') as fp:
        fp.write('return "1"')

    out = run_applescript(testfile)
    assert out.strip() == '1'

    # Test args
    script = """
    on run(argv)
        return first item of argv
    end run
    """
    out = run_applescript(script, 1)
    assert out.strip() == '1'


def test_run_jxa(testfile):
    """Run JXA."""
    script = """
    function run(argv) {
        return "1"
    }
    """

    # Run script passed as text
    out = run_jxa(script)
    assert out.strip() == '1'

    # Run script file
    with open(testfile, 'w') as fp:
        fp.write(script)

    out = run_jxa(testfile)
    assert out.strip() == '1'

    # Test args
    script = """
    function run(argv) {
        return argv[0]
    }
    """
    out = run_jxa(script, 1)
    assert out.strip() == '1'


def test_app_name():
    """Appname"""
    tests = [
        (None, 'com.runningwithcrayons.Alfred'),
        ('', 'com.runningwithcrayons.Alfred'),
        ('4', 'com.runningwithcrayons.Alfred'),
        ('5', 'com.runningwithcrayons.Alfred'),
        ('twelty', 'com.runningwithcrayons.Alfred'),
        ('3', 'Alfred 3'),
        ('3.8', 'Alfred 3'),
        ('3.1-beta', 'Alfred 3'),
        ('3thirty', 'Alfred 3'),
    ]

    for version, wanted in tests:
        with env(alfred_version=version):
            assert jxa_app_name() == wanted, "unexpected appname"


def test_run_trigger(alfred4):
    """Call External Trigger"""
    name = 'test'
    bundleid = 'com.example.workflow'
    arg = 'test arg'

    # With bundle ID
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.runTrigger("test", '
        '{"inWorkflow": "com.example.workflow"});'
    )
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        run_trigger(name, bundleid)
        assert m.cmd == cmd

    # With arg
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.runTrigger("test", '
        '{"inWorkflow": "com.example.workflow", '
        '"withArgument": "test arg"});'
    )
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        run_trigger(name, bundleid, arg)
        assert m.cmd == cmd

    # With bundle ID from env
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.runTrigger("test", '
        '{"inWorkflow": "net.deanishe.alfred-workflow"});'
    )
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        run_trigger(name)
        assert m.cmd == cmd


def test_set_config(alfred4):
    """Set Configuration."""
    name = 'test'
    bundleid = 'com.example.workflow'
    value = 'test'

    # With bundle ID
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.setConfiguration("test", '
        '{"exportable": false, '
        '"inWorkflow": "com.example.workflow", '
        '"toValue": "test"});'
    )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        set_config(name, value, bundleid)
        assert m.cmd == cmd

    # With exportable
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.setConfiguration("test", '
        '{"exportable": true, '
        '"inWorkflow": "com.example.workflow", '
        '"toValue": "test"});'
    )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        set_config(name, value, bundleid, True)
        assert m.cmd == cmd

    # With bundle ID from env
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.setConfiguration("test", '
        '{"exportable": false, '
        '"inWorkflow": "net.deanishe.alfred-workflow", '
        '"toValue": "test"});'
    )
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        set_config(name, value)
        assert m.cmd == cmd


def test_unset_config(alfred4):
    """Unset Configuration."""
    name = 'test'
    bundleid = 'com.example.workflow'

    # With bundle ID
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.removeConfiguration("test", '
        '{"inWorkflow": "com.example.workflow"});'
    )
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        unset_config(name, bundleid)
        assert m.cmd == cmd

    # With bundle ID from env
    os.environ['alfred_workflow_bundleid'] = bundleid
    try:
        cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
        with MockCall() as m:
            unset_config(name)
            assert m.cmd == cmd
    finally:
        del os.environ['alfred_workflow_bundleid']


def test_search_in_alfred(alfred4):
    """Search."""
    query = 'badger, badger, badger'

    # With query
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.search("badger, badger, badger");'
    )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        search_in_alfred(query)
        assert m.cmd == cmd

    # Without query (just opens Alfred)
    script = 'Application("com.runningwithcrayons.Alfred").search("");'

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        search_in_alfred()
        assert m.cmd == cmd


def test_action_in_alfred(alfred4):
    """Action."""
    paths = ['~/Documents', '~/Desktop']

    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.action(["~/Documents", "~/Desktop"]);'
    )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        action_in_alfred(paths)
        assert m.cmd == cmd


def test_browse_in_alfred(alfred4):
    """Browse."""
    path = '~/Documents'
    script = 'Application("com.runningwithcrayons.Alfred").browse("~/Documents");'

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        browse_in_alfred(path)
        assert m.cmd == cmd


def test_reload_workflow(alfred4):
    """Reload workflow."""
    bundleid = 'com.example.workflow'
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.reloadWorkflow("com.example.workflow");'
    )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        reload_workflow(bundleid)
        assert m.cmd == cmd

    # With bundle ID from env
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.reloadWorkflow("net.deanishe.alfred-workflow");'
    )
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        reload_workflow()
        assert m.cmd == cmd


def test_set_theme(alfred4):
    """Set Alfred theme."""
    theme = 'Alfred Dark'
    script = (
        'Application("com.runningwithcrayons.Alfred")'
        '.setTheme("Alfred Dark");'
    )

    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
    with MockCall() as m:
        set_theme(theme)
        assert m.cmd == cmd


def test_appinfo():
    """App info for Safari."""
    for name, bundleid, path in [
        ('Safari', 'com.apple.Safari', '/Applications/Safari.app'),
        ('Console', 'com.apple.Console',
            '/Applications/Utilities/Console.app'),
        # Catalina
        ('Console', 'com.apple.Console',
            '/System/Applications/Utilities/Console.app'),
    ]:

        if not os.path.exists(path):
            continue

        info = appinfo(name)
        assert info is not None, name
        assert info.name == name
        assert info.path == path
        assert info.bundleid == bundleid
        for s in info:
            assert isinstance(s, str)

    # Non-existant app
    info = appinfo("Big, Hairy Man's Special Breakfast Pants")
    assert info is None


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
