#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""Unit tests for Workflow's XML feedback generation."""



from contextlib import contextmanager
from six.moves import StringIO
import sys
from xml.etree import ElementTree as ET

import pytest

from workflow import Workflow


@pytest.fixture(scope='function')
def wf(infopl):
    """Create a :class:`~workflow.Workflow` object."""
    yield Workflow()


@contextmanager
def stdout():
    """Capture output to STDOUT."""
    old = sys.stdout
    sio = StringIO()
    sys.stdout = sio
    yield sio
    sio.close()
    sys.stdout = old


def test_item_creation(wf):
    """XML generation"""
    wf.add_item(
        'title', 'subtitle', arg='arg',
        autocomplete='autocomplete',
        valid=True, uid='uid', icon='icon.png',
        icontype='fileicon',
        type='file', largetext='largetext',
        copytext='copytext',
        quicklookurl='http://www.deanishe.net/alfred-workflow')
    with stdout() as sio:
        wf.send_feedback()
        output = sio.getvalue()

    root = ET.fromstring(output)
    item = list(root)[0]

    assert item.attrib['uid'] == 'uid'
    assert item.attrib['autocomplete'] == 'autocomplete'
    assert item.attrib['valid'] == 'yes'
    assert item.attrib['uid'] == 'uid'

    title, subtitle, arg, icon, \
        largetext, copytext, quicklookurl = list(item)

    assert title.text == 'title'
    assert title.tag == 'title'

    assert subtitle.text == 'subtitle'
    assert subtitle.tag == 'subtitle'

    assert arg.text == 'arg'
    assert arg.tag == 'arg'

    assert largetext.tag == 'text'
    assert largetext.text == 'largetext'
    assert largetext.attrib['type'] == 'largetype'

    assert copytext.tag == 'text'
    assert copytext.text == 'copytext'
    assert copytext.attrib['type'] == 'copy'

    assert icon.text == 'icon.png'
    assert icon.tag == 'icon'
    assert icon.attrib['type'] == 'fileicon'

    assert quicklookurl.tag == 'quicklookurl'
    assert quicklookurl.text == 'http://www.deanishe.net/alfred-workflow'


def test_item_creation_with_modifiers(wf):
    """XML generation (with modifiers)."""
    mod_subs = {}
    for mod in ('cmd', 'ctrl', 'alt', 'shift', 'fn'):
        mod_subs[mod] = mod
    wf.add_item('title', 'subtitle',
                mod_subs,
                arg='arg',
                autocomplete='autocomplete',
                valid=True, uid='uid', icon='icon.png',
                icontype='fileicon',
                type='file')
    with stdout() as sio:
        wf.send_feedback()
        output = sio.getvalue()

    root = ET.fromstring(output)
    item = list(root)[0]
    assert item.attrib['uid'] == 'uid'
    assert item.attrib['autocomplete'] == 'autocomplete'
    assert item.attrib['valid'] == 'yes'
    assert item.attrib['uid'] == 'uid'
    (title, subtitle, sub_cmd, sub_ctrl, sub_alt, sub_shift, sub_fn, arg,
     icon) = list(item)
    assert title.text == 'title'
    assert title.tag == 'title'
    assert subtitle.text == 'subtitle'
    assert sub_cmd.text == 'cmd'
    assert sub_cmd.attrib['mod'] == 'cmd'
    assert sub_ctrl.text == 'ctrl'
    assert sub_ctrl.attrib['mod'] == 'ctrl'
    assert sub_alt.text == 'alt'
    assert sub_alt.attrib['mod'] == 'alt'
    assert sub_shift.text == 'shift'
    assert sub_shift.attrib['mod'] == 'shift'
    assert sub_fn.text == 'fn'
    assert sub_fn.attrib['mod'] == 'fn'
    assert subtitle.tag == 'subtitle'
    assert arg.text == 'arg'
    assert arg.tag == 'arg'
    assert icon.text == 'icon.png'
    assert icon.tag == 'icon'
    assert icon.attrib['type'] == 'fileicon'


def test_item_creation_no_optionals(wf):
    """XML generation (no optionals)"""
    wf.add_item('title')
    with stdout() as sio:
        wf.send_feedback()
        output = sio.getvalue()

    root = ET.fromstring(output)
    item = list(root)[0]
    for key in ['uid', 'arg', 'autocomplete']:
        assert key not in item.attrib

    assert item.attrib['valid'] == 'no'
    title, subtitle = list(item)
    assert title.text == 'title'
    assert title.tag == 'title'
    assert subtitle.text is None
    tags = [elem.tag for elem in list(item)]
    for tag in ['icon', 'arg']:
        assert tag not in tags


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
