#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-22
#

"""Unit tests for notifications."""



import hashlib
import logging
import os
import plistlib
import shutil
import stat
import subprocess

import pytest

from workflow import notify
from workflow.workflow import Workflow

from .conftest import BUNDLE_ID
from .util import (
    FakePrograms,
    WorkflowMock,
)

DATADIR = os.path.expanduser(
    '~/Library/Application Support/Alfred/'
    'Workflow Data/' + BUNDLE_ID)
APP_PATH = os.path.join(DATADIR, 'Notify.app')
APPLET_PATH = os.path.join(APP_PATH, 'Contents/MacOS/applet')
ICON_PATH = os.path.join(APP_PATH, 'Contents/Resources/applet.icns')
INFO_PATH = os.path.join(APP_PATH, 'Contents/Info.plist')

# Alfred-Workflow icon (present in source distribution)
PNG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'icon.png')


@pytest.fixture
def applet():
    """Ensure applet doesn't exist."""
    if os.path.exists(APP_PATH):
        shutil.rmtree(APP_PATH)
    yield
    if os.path.exists(APP_PATH):
        shutil.rmtree(APP_PATH)


def test_log_wf(infopl, alfred4):
    """Workflow and Logger objects correct"""
    wf = notify.wf()
    assert isinstance(wf, Workflow), "not Workflow"
    # Always returns the same objects
    wf2 = notify.wf()
    assert wf is wf2, "not same Workflow"

    log = notify.log()
    assert isinstance(log, logging.Logger), "not Logger"
    log2 = notify.log()
    assert log is log2, "not same Logger"


def test_paths(infopl, alfred4):
    """Module paths are correct"""
    assert DATADIR == notify.wf().datadir, "unexpected datadir"
    assert APPLET_PATH == notify.notifier_program(), "unexpected applet path"
    assert ICON_PATH == notify.notifier_icon_path(), "unexpected icon path"


def test_install(infopl, alfred4, applet):
    """Notify.app is installed correctly"""
    assert os.path.exists(APP_PATH) is False, "APP_PATH exists"
    notify.install_notifier()
    for p in (APP_PATH, APPLET_PATH, ICON_PATH, INFO_PATH):
        assert os.path.exists(p) is True, "path not found"
    # Ensure applet is executable
    assert (os.stat(APPLET_PATH).st_mode & stat.S_IXUSR), \
        "applet not executable"
    # Verify bundle ID was changed
    data = plistlib.readPlist(INFO_PATH)
    bid = data.get('CFBundleIdentifier')
    assert bid != BUNDLE_ID, "bundle IDs identical"
    assert bid.startswith(BUNDLE_ID) is True, "bundle ID not prefix"


def test_sound():
    """Good sounds work, bad ones fail"""
    # Good values
    for s in ('basso', 'GLASS', 'Purr', 'tink'):
        sound = notify.validate_sound(s)
        assert sound is not None
        assert sound == s.title(), "unexpected title"
    # Bad values
    for s in (None, 'SPOONS', 'The Hokey Cokey', ''):
        sound = notify.validate_sound(s)
        assert sound is None


def test_invalid_notifications(infopl, alfred4):
    """Invalid notifications"""
    with pytest.raises(ValueError):
        notify.notify()
    # Is not installed yet
    assert os.path.exists(APP_PATH) is False
    assert notify.notify('Test Title', 'Test Message') is True
    # A notification should appear now, but there's no way of
    # checking whether it worked
    assert os.path.exists(APP_PATH) is True


def test_notifyapp_called(infopl, alfred4):
    """Notify.app is called"""
    c = WorkflowMock()
    notify.install_notifier()
    with c:
        assert notify.notify('Test Title', 'Test Message') is False
        assert c.cmd[0] == APPLET_PATH


@pytest.mark.xfail()
def test_iconutil_fails(infopl, alfred4, tempdir):
    """`iconutil` throws RuntimeError"""
    with FakePrograms('iconutil'):
        icns_path = os.path.join(tempdir, 'icon.icns')
        with pytest.raises(RuntimeError):
            notify.png_to_icns(PNG_PATH, icns_path)


@pytest.mark.xfail()
def test_sips_fails(infopl, alfred4, tempdir):
    """`sips` throws RuntimeError"""
    with FakePrograms('sips'):
        icon_path = os.path.join(tempdir, 'icon.png')
        with pytest.raises(RuntimeError):
            notify.convert_image(PNG_PATH, icon_path, 64)


def test_image_conversion(infopl, alfred4, tempdir, applet):
    """PNG to ICNS conversion"""
    assert os.path.exists(APP_PATH) is False
    notify.install_notifier()
    assert os.path.exists(APP_PATH) is True
    icns_path = os.path.join(tempdir, 'icon.icns')
    assert os.path.exists(icns_path) is False
    notify.png_to_icns(PNG_PATH, icns_path)
    assert os.path.exists(icns_path) is True
    with open(icns_path, 'rb') as fp:
        h1 = hashlib.md5(fp.read())
    with open(ICON_PATH, 'rb') as fp:
        h2 = hashlib.md5(fp.read())
    assert h1.digest() == h2.digest()


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
