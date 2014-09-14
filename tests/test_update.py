#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Fabio Niephaus <fabio.niephaus@gmail.com>, Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#
"""
test_update.py
"""

from __future__ import print_function

import unittest
import os

from workflow import Workflow, update

RELEASE_LATEST = '6.0'
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

TEST_REPO_SLUG = 'deanishe/alfred-workflow-dummy'
EMPTY_REPO_SLUG = 'deanishe/alfred-workflow-empty-dummy'
GH_ROOT = 'https://github.com/' + TEST_REPO_SLUG
GH_API_ROOT = 'https://api.github.com/repos/' + TEST_REPO_SLUG
RELEASES_URL = GH_API_ROOT + '/releases'
URL_DL = GH_ROOT + '/releases/download/v4.0/Dummy-4.0.alfredworkflow'
URL_BAD = 'http://github.com/file.zip'
# INVALID_RELEASE_URL = GH_ROOT + '/releases/download/v3.0/Dummy-3.0.zip'


class UpdateTests(unittest.TestCase):

    def setUp(self):
        self.wf = Workflow()

    def test_download_workflow(self):
        """Update: Download workflow update"""

        with self.assertRaises(ValueError):
            update.download_workflow(URL_BAD)

        local_file = update.download_workflow(URL_DL)

        self.assertTrue(local_file.endswith('.alfredworkflow'))
        self.assertTrue(os.path.isfile(local_file))

    def test_valid_api_url(self):
        """Update: API URL for valid slug"""

        url = update.build_api_url(TEST_REPO_SLUG)
        self.assertEquals(url, RELEASES_URL)

    def test_invalid_api_url(self):
        """Update: API URL for invalid slug"""

        with self.assertRaises(ValueError):
            update.build_api_url('fniephausalfred-workflow')

    def test_empty_repo(self):
        """Update: no releases"""

        with self.assertRaises(ValueError):
            update.check_update(EMPTY_REPO_SLUG, '1.0')

        self.assertEquals(len(update.get_valid_releases(EMPTY_REPO_SLUG)), 0)

    def test_valid_releases(self):
        """Update: valid releases"""

        releases = update.get_valid_releases(TEST_REPO_SLUG)

        # Right number of valid releases
        self.assertEquals(len(releases), 3)

        # Invalid releases are not in list
        versions = [d['version'] for d in releases]
        for v in RELEASES_INVALID:
            self.assertFalse(v in versions)

        # Correct latest release
        self.assertEquals(releases[0]['version'], RELEASE_LATEST)

    def test_version_formats(self):
        """Update: version formats"""

        # Up-to-date versions
        self.assertFalse(update.check_update(TEST_REPO_SLUG, '6.0'))
        self.assertFalse(update.check_update(TEST_REPO_SLUG, 'v6.0'))

        # Old versions
        self.assertTrue(update.check_update(TEST_REPO_SLUG, 'v5.0'))
        self.assertTrue(update.check_update(TEST_REPO_SLUG, '5.0'))

        # Unknown versions
        self.assertTrue(update.check_update(TEST_REPO_SLUG, 'v8.0'))
        self.assertTrue(update.check_update(TEST_REPO_SLUG, '8.0'))

    def test_equal_versions(self):
        """Update: equal versions"""
        # Equal versions
        for l, r in [
                ('1.0', 'v1.0'),
                ('v1.0', '1.0'),
                ('v1.0', 'v1.0'),
                ('1.1.1', 'v1.1.1'),
                ('v1.1.1', '1.1.1'),
                ('v1.1.1', 'v1.1.1'),
                ('dave', 'dave'),
                ('bob', 'bob'),
                ('vernon', 'vernon'),
                ]:
            self.assertFalse(update.is_newer_version(l, r))

        # Unequal versions
        for l, r in [
                ('1.0', 'v1.1'),
                ('v1.0', '1.1'),
                ('v1.0', 'v1.1'),
                ('1.1.1', 'v1.2.1'),
                ('v1.1.1', '1.2.1'),
                ('v1.1.1', 'v1.2.1'),
                ('dave', 'bob'),
                ('bob', 'dave'),
                ('vernon', 'vvernon'),
                ]:
            self.assertTrue(update.is_newer_version(l, r))

    def test_check_update(self):
        """Update: Check update"""

        self.assertTrue(update.check_update(TEST_REPO_SLUG, RELEASE_CURRENT))

        update_info = self.wf.cached_data('__workflow_update_status')
        self.assertFalse(update.check_update(TEST_REPO_SLUG,
                                             update_info['version']))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
