#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-26
#

from __future__ import print_function, unicode_literals, absolute_import

try:
    import xml.etree.cElementTree as ET
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as ET

import pytest

from workflow import feedback


@pytest.fixture
def xmlgen():
    return feedback.XMLGenerator()


def test_item_creation(xmlgen):
    """XML generation"""
    xmlgen.add_item('title', 'subtitle', arg='arg',
                    autocomplete='autocomplete',
                    valid=True, uid='uid', icon='icon.png',
                    icontype='fileicon',
                    type='file', largetext='largetext',
                    copytext='copytext')
    output = xmlgen.xml()
    # from pprint import pprint
    # pprint(output)

    root = ET.fromstring(output)
    item = list(root)[0]

    assert item.attrib['uid'] == 'uid'
    assert item.attrib['autocomplete'] == 'autocomplete'
    assert item.attrib['valid'] == 'yes'
    assert item.attrib['uid'] == 'uid'

    title, subtitle, arg, icon, largetext, copytext = list(item)

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


def test_item_creation_with_modifiers(xmlgen):
    """XML generation (with modifiers)"""
    mod_subs = {}
    for mod in ('cmd', 'ctrl', 'alt', 'shift', 'fn'):
        mod_subs[mod] = mod
    xmlgen.add_item('title', 'subtitle',
                    mod_subs,
                    arg='arg',
                    autocomplete='autocomplete',
                    valid=True, uid='uid', icon='icon.png',
                    icontype='fileicon',
                    type='file')
    output = xmlgen.xml()
    # from pprint import pprint
    # pprint(output)
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


def test_item_creation_no_optionals(xmlgen):
    """XML generation (no optionals)"""
    xmlgen.add_item('title')
    output = str(xmlgen)
    # pprint(output)
    root = ET.fromstring(output)
    item = list(root)[0]
    for key in ['uid', 'arg', 'autocomplete']:
        assert key not in item.attrib
    assert item.attrib['valid'] == 'no'
    title = list(item)[0]
    assert title.text == 'title'
    assert title.tag == 'title'
    tags = [elem.tag for elem in list(item)]
    for tag in ['icon', 'arg']:
        assert tag not in tags


def test_item_creation_icon(xmlgen):
    xmlgen.add_item('title', icon='icon.png')
    output = str(xmlgen)
    root = ET.fromstring(output)
    print(output)
    item = list(root)[0]
    children = list(item)
    assert len(children) == 2
    title, icon = children
    assert title.text == 'title'
    assert icon.text == 'icon.png'
    assert 'type' not in icon.attrib


if __name__ == '__main__':
    pytest.main([__file__])
