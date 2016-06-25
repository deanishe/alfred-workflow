#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Fabio Niephaus <fabio.niephaus@gmail.com>,
# Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#

# TODO: Offline tests using pytest_localserver

"""
test_update_alfred3.py
"""

from __future__ import print_function

import os

import pytest

from util import create_info_plist, delete_info_plist, INFO_PLIST_TEST3
from workflow import update


@pytest.fixture(scope='module')
def info(request):
    """Ensure `info.plist` exists in the working directory."""
    create_info_plist()
    os.environ['alfred_version'] = '2.4'
    update._wf = None
    request.addfinalizer(delete_info_plist)


@pytest.fixture(scope='module')
def info3(request):
    """Ensure `info.plist` exists in the working directory."""
    create_info_plist(INFO_PLIST_TEST3)
    os.environ['alfred_version'] = '3.0.2'
    update._wf = None
    request.addfinalizer(delete_info_plist)


def test_valid_releases_alfred2(info):
    """Valid releases for Alfred 2."""
    # Valid release for 2 & 3
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfredworkflow'}],
                                  'prerelease': False})

    assert r is not None
    assert r['prerelease'] is False
    assert r['download_url'] == 'blah.alfredworkflow'

    # Valid release for 3 only
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfred3workflow'}],
                                  'prerelease': False})

    assert r is None

    # Invalid release
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfred3workflow'},
                                 {'browser_download_url':
                                  'blah2.alfred3workflow'}],
                                  'prerelease': False})

    assert r is None

    # Valid for 2 & 3 with separate workflows
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfredworkflow'},
                                 {'browser_download_url':
                                  'blah.alfred3workflow'}],
                                  'prerelease': False})

    assert r is not None
    assert r['version'] == 'v1.2'
    assert r['download_url'] == 'blah.alfredworkflow'


def test_valid_releases_alfred3(info3):
    """Valid releases for Alfred 3."""
    # Valid release for 2 & 3
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfredworkflow'}],
                                  'prerelease': False})

    assert r is not None
    assert r['download_url'] == 'blah.alfredworkflow'

    # Valid release for 3 only
    print('alfred_version=', os.environ['alfred_version'])
    print('version=', update.wf().alfred_version)
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfred3workflow'}],
                                  'prerelease': False})

    assert r is not None
    assert r['download_url'] == 'blah.alfred3workflow'

    # Invalid release
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfred3workflow'},
                                 {'browser_download_url':
                                  'blah2.alfred3workflow'}],
                                  'prerelease': False})

    assert r is None

    # Valid for 2 & 3 with separate workflows
    r = update._validate_release({'tag_name': 'v1.2', 'assets': [
                                 {'browser_download_url':
                                  'blah.alfredworkflow'},
                                 {'browser_download_url':
                                  'blah.alfred3workflow'}],
                                  'prerelease': False})

    assert r is not None
    assert r['version'] == 'v1.2'
    assert r['download_url'] == 'blah.alfred3workflow'


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
