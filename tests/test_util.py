#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-17
#

"""
"""

from __future__ import print_function, absolute_import

# from collections import namedtuple
import os
import shutil
import subprocess
import tempfile

import pytest

from workflow.util import (
    AS_TRIGGER,
    AS_CONFIG_SET,
    AS_CONFIG_UNSET,
    appinfo,
    applescriptify,
    run_applescript,
    run_command,
    run_jxa,
    run_trigger,
    set_config,
    unicodify,
    unset_config,
    utf8ify,
)


class MockCall(object):
    """Captures calls to `subprocess.check_output`."""

    def __init__(self):
        self.cmd = None
        self._check_output_orig = None

    def set_up(self):
        self._check_output_orig = subprocess.check_output
        subprocess.check_output = self._check_output

    def tear_down(self):
        subprocess.check_output = self._check_output_orig

    def _check_output(self, cmd, **kwargs):
        self.cmd = cmd

    def __enter__(self):
        self.set_up()
        return self

    def __exit__(self, *args):
        self.tear_down()


@pytest.fixture(scope='function')
def testfile(request):
    """Test filepath."""
    tempdir = tempfile.mkdtemp()
    testfile = os.path.join(tempdir, 'testfile')

    def rm():
        shutil.rmtree(tempdir)

    request.addfinalizer(rm)

    return testfile


def test_unicodify():
    """Unicode decoding."""
    data = [
        # input, normalisation form, expected output
        (u'Köln', None, u'Köln'),
        ('Köln', None, u'Köln'),
        (u'Köln', 'NFC', u'K\xf6ln'),
        (u'Köln', 'NFD', u'Ko\u0308ln'),
        ('UTF-8', None, u'UTF-8'),
    ]

    for b, n, x in data:
        s = unicodify(b, norm=n)
        assert s == x
        assert isinstance(s, unicode)


def test_utf8ify():
    """UTF-8 encoding."""
    data = [
        # input, expected output
        (u'Köln', 'Köln'),
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
        (u'no change', u'no change'),
        (u'has "quotes" in it', u'has " & quote & "quotes" & quote & " in it'),
    ]

    for s, x in data:
        r = applescriptify(s)
        assert x == r
        assert isinstance(x, unicode)


def test_run_command():
    """Run command."""
    data = [
        # command, expected output
        ([u'echo', '-n', 1], '1'),
        ([u'echo', '-n', u'Köln'], 'Köln'),
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
    with open(testfile, 'wb') as fp:
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
    with open(testfile, 'wb') as fp:
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


def test_run_trigger():
    """Call External Trigger."""
    name = 'test'
    bundleid = 'net.deanishe.alfred-workflow'
    arg = 'test arg'
    argclause = 'with argument "test arg"'

    # With bundle ID
    script = AS_TRIGGER.format(name=name, bundleid=bundleid, arg='')
    cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
    with MockCall() as m:
        run_trigger(name, bundleid)
        assert m.cmd == cmd

    # With arg
    script = AS_TRIGGER.format(name=name, bundleid=bundleid, arg=argclause)
    cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
    with MockCall() as m:
        run_trigger(name, bundleid, arg)
        assert m.cmd == cmd

    # With bundle ID from env
    os.environ['alfred_workflow_bundleid'] = bundleid
    try:
        script = AS_TRIGGER.format(name=name, bundleid=bundleid, arg='')
        cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
        with MockCall() as m:
            run_trigger(name)
            assert m.cmd == cmd
    finally:
        del os.environ['alfred_workflow_bundleid']


def test_set_config():
    """Set Configuration."""
    name = 'test'
    bundleid = 'net.deanishe.alfred-workflow'
    value = 'test'
    # argclause = 'with argument "test arg"'

    # With bundle ID
    script = AS_CONFIG_SET.format(name=name, value=value,
                                  bundleid=bundleid,
                                  export='exportable false')

    cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
    with MockCall() as m:
        set_config(name, value, bundleid)
        assert m.cmd == cmd

    # With exportable
    script = AS_CONFIG_SET.format(name=name, value=value,
                                  bundleid=bundleid,
                                  export='exportable true')

    cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
    with MockCall() as m:
        set_config(name, value, bundleid, True)
        assert m.cmd == cmd

    # With bundle ID from env
    os.environ['alfred_workflow_bundleid'] = bundleid
    try:
        script = AS_CONFIG_SET.format(name=name, value=value,
                                      bundleid=bundleid,
                                      export='exportable false')

        cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
        with MockCall() as m:
            set_config(name, value)
            assert m.cmd == cmd
    finally:
        del os.environ['alfred_workflow_bundleid']


def test_unset_config():
    """Unset Configuration."""
    name = 'test'
    bundleid = 'net.deanishe.alfred-workflow'
    value = 'test'
    # argclause = 'with argument "test arg"'

    # With bundle ID
    script = AS_CONFIG_UNSET.format(name=name, bundleid=bundleid)

    cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
    with MockCall() as m:
        unset_config(name, bundleid)
        assert m.cmd == cmd

    # With bundle ID from env
    os.environ['alfred_workflow_bundleid'] = bundleid
    try:
        script = AS_CONFIG_UNSET.format(name=name, bundleid=bundleid)

        cmd = ['/usr/bin/osascript', '-l', 'AppleScript', '-e', script]
        with MockCall() as m:
            unset_config(name)
            assert m.cmd == cmd
    finally:
        del os.environ['alfred_workflow_bundleid']


def test_appinfo():
    """App info for Safari."""
    for name, bundleid, path in [
        (u'Safari', u'com.apple.Safari', u'/Applications/Safari.app'),
        (u'Digital Color Meter', u'com.apple.DigitalColorMeter',
         u'/Applications/Utilities/Digital Color Meter.app'),
    ]:

        info = appinfo(name)
        assert info is not None
        assert info.name == name
        assert info.path == path
        assert info.bundleid == bundleid
        for s in info:
            assert isinstance(s, unicode)

    # Non-existant app
    info = appinfo("Big, Hairy Man's Special Breakfast Pants")
    assert info is None


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
