#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#

"""Unit tests for update mechanism."""



from contextlib import contextmanager
import os
import re

import pytest
import pytest_localserver  # noqa: F401

from .util import WorkflowMock
from workflow import Workflow, update
from workflow.update import Download, Version
from unittest.mock import patch
import requests

# Where test data is
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# GitHub API JSON for test repos
# An empty list
RELEASES_JSON_EMPTY = '[]'
# A list of valid and invalid releases. The below variables
# refer to these data.
RELEASES_JSON = open(os.path.join(DATA_DIR, 'gh-releases.json')).read()
RELEASES_4PLUS_JSON = open(
    os.path.join(DATA_DIR, 'gh-releases-4plus.json')).read()
# A dummy Alfred workflow
DATA_WORKFLOW = open(
    os.path.join(DATA_DIR, 'Dummy-6.0.alfredworkflow'), 'rb').read()

# Alfred 4
RELEASE_LATEST = '9.0'
RELEASE_LATEST_PRERELEASE = '10.0-beta'
# Alfred 3
RELEASE_LATEST_V3 = '6.0'
RELEASE_LATEST_PRERELEASE_V3 = '7.1-beta'
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
TEST_REPO = 'deanishe/alfred-workflow-dummy'
EMPTY_REPO = 'deanishe/alfred-workflow-empty-dummy'
GH_ROOT = 'https://github.com/' + TEST_REPO
GH_API_ROOT = 'https://api.github.com/repos/' + TEST_REPO
RELEASES_URL = GH_API_ROOT + '/releases'
URL_DL = 'https://github.com/releases/download/v6.0/Dummy-6.0.alfredworkflow'
URL_BAD = 'http://github.com/file.zip'
# INVALID_RELEASE_URL = GH_ROOT + '/releases/download/v3.0/Dummy-3.0.zip'

DL_BAD = Download(url='http://github.com/file.zip',
                  filename='file.zip',
                  version=Version('0'))


@contextmanager
def fakeresponse(httpserver, content, headers=None):
    """Monkey patch `web.request()` to return the specified response."""
    httpserver.serve_content(content, headers=headers)
    orig = requests.request

    def _request(*args, **kwargs):
        """Replace request URL with `httpserver` URL"""
        new_args = (args[0], httpserver.url) + args[2:]
        print('intercept', args, kwargs, '->', new_args)
        return orig(*new_args, **kwargs)

    with patch('requests.api.request', _request):
        yield


def test_parse_releases(infopl, alfred4):
    """Parse releases JSON"""
    dls = Download.from_releases(RELEASES_JSON)
    assert len(dls) == len(VALID_DOWNLOADS), "wrong no. of downloads"

    for i, dl in enumerate(dls):
        print(('dl=%r, x=%r' % (dl, VALID_DOWNLOADS[i])))
        assert dl == VALID_DOWNLOADS[i], "different downloads"


def test_compare_downloads():
    """Compare Downloads"""
    dl = Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v11/Dummy-11.0.alfredworkflow",  # noqa: E501
                  "Dummy-11.0.alfredworkflow",
                  "v11",
                  False)

    for other in VALID_DOWNLOADS:
        assert dl > other, "unexpected comparison"
        assert dl != other, "unexpected equality"


def test_bad_download_url(infopl, alfred4):
    """Bad update download URL"""
    with pytest.raises(ValueError):
        update.retrieve_download(DL_BAD)


def test_valid_api_url(infopl, alfred4):
    """API URL for valid slug"""
    url = update.build_api_url(TEST_REPO)
    assert url == RELEASES_URL


def test_invalid_api_url(infopl, alfred4):
    """API URL for invalid slug"""
    with pytest.raises(ValueError):
        update.build_api_url('fniephausalfred-workflow')


def test_empty_repo(httpserver, infopl):
    """No releases"""
    with fakeresponse(httpserver, RELEASES_JSON_EMPTY, HTTP_HEADERS_JSON):
        update.check_update(EMPTY_REPO, '1.0')
        assert len(update.get_downloads(EMPTY_REPO)) == 0


def test_valid_downloads(httpserver, infopl, alfred4):
    """Valid downloads"""
    with fakeresponse(httpserver, RELEASES_JSON, HTTP_HEADERS_JSON):
        dls = update.get_downloads(TEST_REPO)

    assert len(dls) == len(VALID_DOWNLOADS), "wrong no. of downloads"

    for i, dl in enumerate(dls):
        print(('dl=%r, x=%r' % (dl, VALID_DOWNLOADS[i])))
        assert dl == VALID_DOWNLOADS[i], "different downloads"


def test_latest_download(infopl):
    """Latest download for Alfred version."""
    dls = Download.from_releases(RELEASES_JSON)
    tests = (
        # downloads, alfred version, prereleases, wanted result
        ([], None, False, None),
        (dls, None, False, '9.0'),
        (dls, None, True, '10.0-beta'),
        (dls, '4', False, '9.0'),
        (dls, '4', True, '10.0-beta'),
        (dls, '3', False, '6.0'),
        (dls, '3', True, '10.0-beta'),
    )

    for data, version, pre, wanted in tests:
        dl = update.latest_download(data, version, pre)
        if wanted is None:
            assert dl is None, "latest is not None"
        else:
            assert dl.version == Version(wanted), "unexpected version"


def test_version_formats(httpserver, infopl, alfred4):
    """Version formats"""
    tests = (
        # current version, prereleases, alfred version, expected value
        ('6.0', False, None, True),
        ('6.0', False, '4', True),
        ('6.0', False, '3', False),
        ('6.0', True, None, True),
        ('6.0', True, '4', True),
        ('6.0', True, '3', True),
        ('9.0', False, None, False),
        ('9.0', False, '4', False),
        ('9.0', False, '3', False),
        ('9.0', True, None, True),
        ('9.0', True, '4', True),
        ('9.0', True, '3', True),
    )

    with fakeresponse(httpserver, RELEASES_JSON, HTTP_HEADERS_JSON):
        for current, pre, alfred, wanted in tests:
            v = update.check_update(TEST_REPO, current, pre, alfred)
            assert v == wanted, "unexpected update status"


def test_check_update(httpserver, infopl, alfred4):
    """Check update"""
    key = '__workflow_latest_version'
    tests = [
        # data, alfred version, pre, expected value
        (RELEASES_JSON, None, False, True),
        (RELEASES_JSON, '3', False, True),
        (RELEASES_4PLUS_JSON, None, False, True),
        (RELEASES_4PLUS_JSON, '3', False, False),
        (RELEASES_4PLUS_JSON, '3', True, False),
    ]

    for data, alfred, pre, wanted in tests:
        wf = Workflow()
        wf.reset()

        with fakeresponse(httpserver, data, HTTP_HEADERS_JSON):
            v = update.check_update(TEST_REPO, RELEASE_CURRENT,
                                    pre, alfred)
            assert v == wanted, "unexpected update status"

            status = wf.cached_data(key)
            assert status is not None
            assert status['available'] == wanted
            assert wf.update_available == wanted

            if wanted:  # other data may not be set if available is False
                v = update.check_update(TEST_REPO, status['version'],
                                        pre, alfred)
                assert v is False


def test_install_update(httpserver, infopl, alfred4):
    """Update is installed."""
    key = '__workflow_latest_version'
    # Clear any cached data
    wf = Workflow()
    wf.reset()

    # Assert cache was cleared
    assert wf.cached_data(key) is None

    with fakeresponse(httpserver, RELEASES_JSON, HTTP_HEADERS_JSON):
        # No update because no update status has been cached
        assert update.install_update() is False

        # Check for updates
        v = update.check_update(TEST_REPO, RELEASE_CURRENT)
        assert v is True

        # Verify new workflow is downloaded and installed
        with WorkflowMock() as c:
            assert update.install_update() is True
            assert c.cmd[0] == 'open'
            assert re.search(r'\.alfred(\d+)?workflow$', c.cmd[1])

        assert wf.cached_data(key)['available'] is False

        # Test mangled update data
        status = wf.cached_data(key)
        assert status['available'] is False
        assert status['download'] is None
        assert status['version'] is None
        # Flip available bit, but leave rest invalid
        status['available'] = True
        wf.cache_data(key, status)

        with WorkflowMock():
            assert update.install_update() is False


def test_no_auto_update(infopl, alfred4):
    """No update check."""
    key = '__workflow_latest_version'
    wf = Workflow()
    wf.reset()
    # Assert cache was cleared
    assert wf.cached_data(key) is None

    c = WorkflowMock(['script', 'workflow:noautoupdate'])
    with c:
        wf = Workflow()
        wf.args
        assert wf.settings.get('__workflow_autoupdate') is False
        assert wf.cached_data(key) is None

    c = WorkflowMock()
    with c:
        wf = Workflow(update_settings={
            'github_slug': TEST_REPO,
            'version': RELEASE_CURRENT
        })

        assert wf.cached_data(key) is None


def test_update_nondefault_serialiser(httpserver, infopl, alfred4):
    """Check update works when a custom serialiser is set on Workflow

    https://github.com/deanishe/alfred-workflow/issues/113
    """
    wf = Workflow()
    wf.cache_serializer = 'json'
    wf.reset()

    with fakeresponse(httpserver, RELEASES_JSON, HTTP_HEADERS_JSON):
        assert update.check_update(TEST_REPO,
                                   RELEASE_CURRENT) is True

        assert wf.update_available is True


VALID_DOWNLOADS = [
    # Latest version for Alfred 4
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v10.0-beta/Dummy-10.0-beta.alfredworkflow",  # noqa: E501
             "Dummy-10.0-beta.alfredworkflow",
             "v10.0-beta",
             True),
    # Latest stable version for Alfred 4
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v9.0/Dummy-9.0.alfred4workflow",  # noqa: E501
             "Dummy-9.0.alfred4workflow",
             "v9.0",
             False),
    # Latest version for Alfred 3
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v7.1.0-beta/Dummy-7.1-beta.alfredworkflow",  # noqa: E501
             "Dummy-7.1-beta.alfredworkflow",
             "v7.1.0-beta",
             True),
    # Latest stable version for Alfred 3
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v6.0/Dummy-6.0.alfred4workflow",  # noqa: E501
             "Dummy-6.0.alfred4workflow",
             "v6.0",
             False),
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v6.0/Dummy-6.0.alfred3workflow",  # noqa: E501
             "Dummy-6.0.alfred3workflow",
             "v6.0",
             False),
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v6.0/Dummy-6.0.alfredworkflow",  # noqa: E501
             "Dummy-6.0.alfredworkflow",
             "v6.0",
             False),
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v2.0/Dummy-2.0.alfredworkflow",  # noqa: E501
             "Dummy-2.0.alfredworkflow",
             "v2.0",
             False),
    Download("https://github.com/deanishe/alfred-workflow-dummy/releases/download/v1.0/Dummy-1.0.alfredworkflow",  # noqa: E501
             "Dummy-1.0.alfredworkflow",
             "v1.0",
             False),
]


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
