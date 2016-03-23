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
test_update.py
"""

from __future__ import print_function

from contextlib import contextmanager
import unittest
import os
import time

import pytest
import pytest_localserver

from util import WorkflowMock, create_info_plist, delete_info_plist
from workflow import Workflow, update
from workflow.background import is_running
from workflow import web

# Where test data is
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# GitHub API JSON for test repos
DATA_JSON_EMPTY_PATH = os.path.join(DATA_DIR, 'gh-releases-empty.json')
DATA_JSON_PATH = os.path.join(DATA_DIR, 'gh-releases.json')
DATA_WORKFLOW_PATH = os.path.join(DATA_DIR, 'Dummy-6.0.alfredworkflow')

# A dummy Alfred workflow
DATA_WORKFLOW = open(DATA_WORKFLOW_PATH).read()
# An empty list
DATA_JSON_EMPTY = open(DATA_JSON_EMPTY_PATH).read()
# A list of valid and invalid releases. The below variables
# refer to these data.
DATA_JSON = open(DATA_JSON_PATH).read()

RELEASE_LATEST = '6.0'
RELEASE_LATEST_PRERELEASE = '7.1-beta'
RELEASE_OLDEST = '1.0'
# Use this as current version
RELEASE_CURRENT = '2.0'
# v3.0 contains a .zip file, not an .alfredworkflow file
RELEASES_INVALID = (
    '3.0',  # No .alfredworkflow file
    '4.0',  # 2 .alfredworkflow files
    '5.0',  # No files
    '7.0',  # No files
)

HTTP_HEADERS_JSON = {
    'Content-Type': 'application/json; charset=utf-8',
}

# This repo was created especially to test Alfred-Workflow
# It contains multiple releases, some valid, some invalid
# The .alfredworkflow files in the releases are working demos.
#
# The repo has since been mirrored to the `tests/data` directory
# (see DATA_* variables above), so the tests can run offline.
TEST_REPO_SLUG = 'deanishe/alfred-workflow-dummy'
EMPTY_REPO_SLUG = 'deanishe/alfred-workflow-empty-dummy'
GH_ROOT = 'https://github.com/' + TEST_REPO_SLUG
GH_API_ROOT = 'https://api.github.com/repos/' + TEST_REPO_SLUG
RELEASES_URL = GH_API_ROOT + '/releases'
# URL_DL = GH_ROOT + '/releases/download/v4.0/Dummy-4.0.alfredworkflow'
URL_DL = GH_ROOT + '/releases/download/v6.0/Dummy-6.0.alfredworkflow'
URL_BAD = 'http://github.com/file.zip'
# INVALID_RELEASE_URL = GH_ROOT + '/releases/download/v3.0/Dummy-3.0.zip'


@pytest.fixture(scope='module')
def info(request):
    """Ensure `info.plist` exists in the working directory."""
    create_info_plist()
    request.addfinalizer(delete_info_plist)


@contextmanager
def fakeresponse(server, content, headers=None):
    """Monkey patch `web.request()` to return the specified response."""
    orig = web.request
    server.serve_content(content, headers=headers)

    def _request(*args, **kwargs):
        """Replace request URL with `httpserver` URL"""
        print('requested URL={0!r}'.format(args[1]))
        args = (args[0], server.url) + args[2:]
        print('request args={0!r}'.format(args))
        return orig(*args, **kwargs)

    web.request = _request
    yield
    web.request = orig


def test_download_workflow(httpserver, info):
    """Download workflow update"""
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename=Dummy-6.0.alfredworkflow',
    }
    with fakeresponse(httpserver, DATA_WORKFLOW, headers):
        local_file = update.download_workflow(URL_DL)
        assert local_file.endswith('.alfredworkflow')
        assert os.path.isfile(local_file) is True


def test_bad_download_url(info):
    """Bad update download URL"""
    with pytest.raises(ValueError):
        update.download_workflow(URL_BAD)


def test_valid_api_url(info):
    """API URL for valid slug"""
    url = update.build_api_url(TEST_REPO_SLUG)
    assert url == RELEASES_URL


def test_invalid_api_url(info):
    """API URL for invalid slug"""
    with pytest.raises(ValueError):
        update.build_api_url('fniephausalfred-workflow')


def test_empty_repo(httpserver, info):
    """No releases"""
    # with webget(httpserver.url):
    with fakeresponse(httpserver, DATA_JSON_EMPTY, HTTP_HEADERS_JSON):
        with pytest.raises(ValueError):
            update.check_update(EMPTY_REPO_SLUG, '1.0')
        assert len(update.get_valid_releases(EMPTY_REPO_SLUG)) == 0


def test_valid_releases(httpserver, info):
    """Valid releases"""
    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        releases = update.get_valid_releases(TEST_REPO_SLUG)
        # Correct number of releases
        assert len(releases) == 3

        # Invalid releases are not in the list
        versions = [d['version'] for d in releases]
        for v in RELEASES_INVALID:
            assert v not in versions

        # Correct latest release
        assert update.Version(releases[0]['version']) == \
            update.Version(RELEASE_LATEST)

def test_valid_releases_with_prereleases(httpserver, info):
    """Valid releases with prereleases"""
    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        releases = update.get_valid_releases(TEST_REPO_SLUG, prereleases=True)

        # Correct number of releases
        assert len(releases) == 4

        # Invalid releases are not in the list
        versions = [d['version'] for d in releases]
        for v in RELEASES_INVALID:
            assert v not in versions

        # Correct latest release
        assert update.Version(releases[0]['version']) == \
            update.Version(RELEASE_LATEST_PRERELEASE)


def test_version_formats(httpserver, info):
    """Version formats"""

    falsey = (
        # Up-to-date versions
        '6.0', 'v6.0',
        # Unknown versions
        'v8.0', '8.0',
    )
    truthy = (
        # Old versions
        'v5.0', '5.0',
    )

    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        for vstr in falsey:
            assert update.check_update(TEST_REPO_SLUG, vstr) is False
        for vstr in truthy:
            assert update.check_update(TEST_REPO_SLUG, vstr) is True


def test_prerelease_version_formats(httpserver, info):
    """Prerelease version formats"""

    falsey = (
        # Up-to-date versions
        '7.1.0-beta', 'v7.1.0-beta',
        # Unknown versions
        'v8.0', '8.0',
    )
    truthy = (
        # Old versions
        'v5.0', '5.0',
    )

    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        for vstr in falsey:
            assert update.check_update(TEST_REPO_SLUG, vstr, prereleases=True) is False
        for vstr in truthy:
            assert update.check_update(TEST_REPO_SLUG, vstr, prereleases=True) is True


def test_check_update(httpserver, info):
    """Check update"""
    wf = Workflow()
    wf.reset()

    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        assert update.check_update(TEST_REPO_SLUG,
                                   RELEASE_CURRENT) is True

        update_info = wf.cached_data('__workflow_update_status')
        assert update_info is not None
        assert wf.update_available is True

        assert update.check_update(TEST_REPO_SLUG,
                                   update_info['version']) is False


def test_check_update_with_prereleases(httpserver, info):
    """Check update with prereleases"""
    wf = Workflow()
    wf.reset()

    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        assert update.check_update(TEST_REPO_SLUG,
                                   RELEASE_CURRENT,
                                   prereleases=True) is True

        update_info = wf.cached_data('__workflow_update_status')
        assert update_info is not None
        assert wf.update_available is True

        assert update.check_update(TEST_REPO_SLUG,
                                   update_info['version'],
                                   prereleases=True) is False


def test_install_update(httpserver, info):
    """Update is installed"""
    # Clear any cached data
    wf = Workflow()
    wf.reset()

    # Assert cache was cleared
    assert wf.cached_data('__workflow_update_status') is None

    with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
        # No update for latest release
        assert update.install_update(TEST_REPO_SLUG, RELEASE_LATEST) is False

        # Check for updates
        assert update.check_update(TEST_REPO_SLUG, RELEASE_CURRENT) is True

        # Verify new workflow is downloaded and installed
        c = WorkflowMock()
        with c:
            assert update.install_update(TEST_REPO_SLUG,
                                         RELEASE_CURRENT) is True

        assert c.cmd[0] == 'open'
        assert c.cmd[1].endswith('.alfredworkflow')
        assert wf.cached_data(
            '__workflow_update_status')['available'] is False


def test_no_auto_update(info):
    """No update check"""
    wf = Workflow()
    wf.reset()
    # Assert cache was cleared
    assert wf.cached_data('__workflow_update_status') is None

    c = WorkflowMock(['script', 'workflow:noautoupdate'])
    with c:
        wf = Workflow()
        wf.args
        assert wf.settings.get('__workflow_autoupdate') is False
        assert wf.cached_data('__workflow_update_status') is None

    c = WorkflowMock()
    with c:
        wf = Workflow(update_settings={
            'github_slug': TEST_REPO_SLUG,
            'version': RELEASE_CURRENT
        })

        assert wf.cached_data('__workflow_update_status') is None


# def test_workflow_update_methods(httpserver, info):
#     """Workflow update methods"""

#     def fake(wf):
#         return

#     with fakeresponse(httpserver, DATA_JSON, HTTP_HEADERS_JSON):
#         Workflow().reset()
#         # Initialise with outdated version
#         wf = Workflow(update_settings={
#             'github_slug': 'deanishe/alfred-workflow-dummy',
#             'version': 'v1.0',
#             'frequency': 1,
#         })

#         wf.run(fake)

#         # Check shouldn't have completed yet
#         assert wf.update_available is False

#         # Wait for background update check
#         assert is_running('__workflow_update_check') is True
#         while is_running('__workflow_update_check'):
#             time.sleep(0.5)
#         time.sleep(1)

#         # There *is* a newer version in the repo
#         print(repr(wf.cached_data('__workflow_update_status', max_age=0)))
#         assert wf.update_available is True

#         # Mock out subprocess and check the correct command is run
#         c = WorkflowMock()
#         with c:
#             assert wf.start_update() is True
#         # wf.logger.debug('start_update : {}'.format(c.cmd))
#         assert c.cmd[0] == '/usr/bin/python'
#         assert c.cmd[2] == '__workflow_update_install'

#         # Grab the updated release data, then reset the cache
#         update_info = wf.cached_data('__workflow_update_status')

#         wf.reset()

#         # Initialise with latest available release
#         wf = Workflow(update_settings={
#             'github_slug': 'deanishe/alfred-workflow-dummy',
#             'version': update_info['version'],
#         })

#         wf.run(fake)

#         # Wait for background update check
#         assert is_running('__workflow_update_check') is True
#         while is_running('__workflow_update_check'):
#             time.sleep(0.05)

#         # Remote version is same as the one we passed to Workflow
#         assert wf.update_available is False
#         assert wf.start_update() is False

#         wf.reset()

#         # Initialise with outdated version allowing pre-release updates
#         wf = Workflow(update_settings={
#             'github_slug': 'deanishe/alfred-workflow-dummy',
#             'version': 'v1.0',
#             'frequency': 1,
#             'prereleases': True,
#         })

#         wf.run(fake)

#         # Check shouldn't have completed yet
#         assert wf.update_available is False

#         # Wait for background update check
#         assert is_running('__workflow_update_check') is True
#         while is_running('__workflow_update_check'):
#             time.sleep(0.5)
#         time.sleep(1)

#         # There *is* a newer version in the repo
#         print(repr(wf.cached_data('__workflow_update_status', max_age=0)))
#         assert wf.update_available is True

#         # Mock out subprocess and check the correct command is run
#         c = WorkflowMock()
#         with c:
#             assert wf.start_update() is True
#         # wf.logger.debug('start_update : {}'.format(c.cmd))
#         assert c.cmd[0] == '/usr/bin/python'
#         assert c.cmd[2] == '__workflow_update_install'

#         # Grab the updated release data, then reset the cache
#         update_info = wf.cached_data('__workflow_update_status')

#         wf.reset()

#         # Initialise with latest available release allowing pre-release updates
#         wf = Workflow(update_settings={
#             'github_slug': 'deanishe/alfred-workflow-dummy',
#             'version': update_info['version'],
#             'prereleases': True,
#         })

#         wf.run(fake)

#         # Wait for background update check
#         assert is_running('__workflow_update_check') is True
#         while is_running('__workflow_update_check'):
#             time.sleep(0.05)

#         # Remote version is same as the one we passed to Workflow
#         assert wf.update_available is False
#         assert wf.start_update() is False


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
