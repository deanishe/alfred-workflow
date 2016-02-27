#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-27
#

from __future__ import print_function

from contextlib import contextmanager

import pytest

from workflow import Workflow

from util import WorkflowMock, create_info_plist, delete_info_plist


UPDATE_SETTINGS = {
    'github_slug': 'deanishe/alfred-workflow-dummy',
    'version': 'v2.0',
    'frequency': 1,
}


@contextmanager
def dummy(*args, **kwargs):
    yield None


@contextmanager
def ctx(args=None, update_settings=None, clear=True):
    update_settings = update_settings or UPDATE_SETTINGS
    args = args or []
    c = dummy()
    if args:
        # Add placeholder for ARGV[0]
        args = ['script'] + args
    create_info_plist()
    if args:
        c = WorkflowMock(args)
    with c:
        wf = Workflow(update_settings=update_settings)
        yield wf, c
    if clear:
        wf.reset()
        delete_info_plist()


def test_auto_update():
    """Auto-update toggle active"""

    def fake(wf):
        return

    with ctx(['workflow:autoupdate']) as (wf, c):
        print('wf={0!r}, c={1!r}'.format(wf, c))
        wf.args
        print('wf.args={0!r}'.format(wf.args))
        wf.run(fake)
        assert wf.settings.get('__workflow_autoupdate') is True

    with ctx(['workflow:noautoupdate']) as (wf, c):
        wf.args
        wf.run(fake)
        assert wf.settings.get('__workflow_autoupdate') is False
        print('update_available={0!r}'.format(wf.update_available))


def test_update():
    """Auto-update installs update"""

    def fake(wf):
        return

    with ctx() as (wf, c):
        wf.run(fake)
        assert wf.update_available is False

    # Mock subprocess.call etc. so the script doesn't try to
    # update the workflow in Alfred
    with ctx(['workflow:update'], clear=False) as (wf, c):
        wf.run(fake)
        wf.args

        print('Magic update command : {0!r}'.format(c.cmd))

        assert c.cmd[0] == '/usr/bin/python'
        assert c.cmd[2] == '__workflow_update_install'

    update_settings = UPDATE_SETTINGS.copy()
    update_settings['version'] = 'v6.0'
    with ctx(['workflow:update'], update_settings) as (wf, c):
        wf.run(fake)
        wf.args

        # Update command wasn't called
        assert c.cmd == ()


def test_update_turned_off():
    """Auto-update turned off"""

    # Check update isn't performed if user has turned off
    # auto-update

    def fake(wf):
        return

    with ctx() as (wf, c):
        wf.settings['__workflow_autoupdate'] = False
        assert wf.check_update() is None


if __name__ == '__main__':
    pytest.main([__file__])
