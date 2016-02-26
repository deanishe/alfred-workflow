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
"""
test_update.py
"""

from __future__ import print_function

import unittest
import os
import time

from util import WorkflowMock, create_info_plist, delete_info_plist
from workflow import Workflow, update
from workflow.background import is_running

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

# This repo was created especially to test Alfred-Workflow
# It contains multiple releases, some valid, some invalid
# The .alfredworkflow files in the releases are working demos
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
        create_info_plist()
        self.wf = Workflow()

    def tearDown(self):
        delete_info_plist()

    def test_download_workflow(self):
        """Update: Download workflow update"""

        self.assertRaises(ValueError, update.download_workflow, URL_BAD)

        local_file = update.download_workflow(URL_DL)

        self.assertTrue(local_file.endswith('.alfredworkflow'))
        self.assertTrue(os.path.isfile(local_file))

    def test_valid_api_url(self):
        """Update: API URL for valid slug"""

        url = update.build_api_url(TEST_REPO_SLUG)
        self.assertEquals(url, RELEASES_URL)

    def test_invalid_api_url(self):
        """Update: API URL for invalid slug"""

        self.assertRaises(ValueError, update.build_api_url,
                          'fniephausalfred-workflow')

    def test_empty_repo(self):
        """Update: no releases"""

        self.assertRaises(ValueError, update.check_update,
                          EMPTY_REPO_SLUG, '1.0')

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
        self.assertEquals(update.Version(releases[0]['version']),
                          update.Version(RELEASE_LATEST))

    def test_valid_releases_with_prereleases(self):
        """Update: valid releases with prereleases"""

        releases = update.get_valid_releases(TEST_REPO_SLUG, prereleases=True)

        # Right number of valid releases
        self.assertEquals(len(releases), 4)

        # Invalid releases are not in list
        versions = [d['version'] for d in releases]
        for v in RELEASES_INVALID:
            self.assertFalse(v in versions)

        # Correct latest release
        self.assertEquals(update.Version(releases[0]['version']),
                          update.Version(RELEASE_LATEST_PRERELEASE))

    def test_version_formats(self):
        """Update: version formats"""

        # Up-to-date versions
        self.assertFalse(update.check_update(TEST_REPO_SLUG, '6.0'))
        self.assertFalse(update.check_update(TEST_REPO_SLUG, 'v6.0'))

        # Up-to-date pre-release versions
        self.assertFalse(update.check_update(TEST_REPO_SLUG, '7.1-beta', prereleases=True))
        self.assertFalse(update.check_update(TEST_REPO_SLUG, 'v7.1-beta', prereleases=True))

        # Old versions
        self.assertTrue(update.check_update(TEST_REPO_SLUG, 'v5.0'))
        self.assertTrue(update.check_update(TEST_REPO_SLUG, '5.0'))

        # Unknown versions
        self.assertFalse(update.check_update(TEST_REPO_SLUG, 'v8.0'))
        self.assertFalse(update.check_update(TEST_REPO_SLUG, '8.0'))

    def test_check_update(self):
        """Update: Check update with prereleases"""

        self.assertTrue(update.check_update(TEST_REPO_SLUG, RELEASE_CURRENT))

        update_info = self.wf.cached_data('__workflow_update_status')
        self.assertFalse(update.check_update(TEST_REPO_SLUG,
                                             update_info['version']))

    def test_check_update_with_prereleases(self):
        """Update: Check update"""

        self.assertTrue(update.check_update(TEST_REPO_SLUG, RELEASE_CURRENT, prereleases=True))

        update_info = self.wf.cached_data('__workflow_update_status')
        self.assertFalse(update.check_update(TEST_REPO_SLUG,
                                             update_info['version'],
                                             prereleases=True))

    def test_install_update(self):
        """Update: installs update"""

        # Make sure there's no cached update data
        wf = Workflow()
        wf.reset()

        # Verify that there's no update available
        self.assertTrue(wf.cached_data('__workflow_update_status') is None)

        self.assertFalse(update.install_update(TEST_REPO_SLUG,
                                               RELEASE_LATEST))

        # Get new update data
        self.assertTrue(update.check_update(TEST_REPO_SLUG, RELEASE_CURRENT))

        # Verify new workflow is downloaded and installed
        c = WorkflowMock()
        with c:
            self.assertTrue(update.install_update(TEST_REPO_SLUG,
                                                  RELEASE_CURRENT))
        self.assertEquals(c.cmd[0], 'open')
        self.assertTrue(c.cmd[1].endswith('.alfredworkflow'))

        self.assertFalse(wf.cached_data(
                         '__workflow_update_status')['available'])

    def test_no_auto_update(self):
        """Update: no update check"""

        # Make sure there's no cached update data
        wf = Workflow()
        wf.reset()

        self.assertTrue(self.wf.cached_data('__workflow_update_status') is
                        None)

        wf = Workflow()
        c = WorkflowMock(['script', 'workflow:noautoupdate'])
        with c:
            wf.args
        self.assertFalse(wf.settings.get('__workflow_autoupdate'))

        self.assertTrue(self.wf.cached_data('__workflow_update_status') is
                        None)

        c = WorkflowMock()
        with c:
            wf = Workflow(update_settings={'github_slug': TEST_REPO_SLUG,
                          'version': RELEASE_CURRENT})

        self.assertTrue(self.wf.cached_data('__workflow_update_status') is
                        None)

    def test_workflow_update_methods(self):
        """Workflow update methods"""

        def fake(wf):
            return

        Workflow().reset()
        # Initialise with outdated version
        wf = Workflow(update_settings={
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'frequency': 1,
        })

        wf.run(fake)

        # Check won't have completed yet
        self.assertFalse(wf.update_available)

        # wait for background update check
        self.assertTrue(is_running('__workflow_update_check'))
        while is_running('__workflow_update_check'):
            time.sleep(0.05)
        time.sleep(1)

        # There *is* a newer version in the repo
        self.assertTrue(wf.update_available)

        # Mock out subprocess and check the correct command is run
        c = WorkflowMock()
        with c:
            self.assertTrue(wf.start_update())
        # wf.logger.debug('start_update : {}'.format(c.cmd))
        self.assertEquals(c.cmd[0], '/usr/bin/python')
        self.assertEquals(c.cmd[2], '__workflow_update_install')

        # Grab the updated release data, then reset the cache
        update_info = wf.cached_data('__workflow_update_status')

        wf.reset()

        # Initialise with latest available release
        wf = Workflow(update_settings={
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': update_info['version'],
        })

        wf.run(fake)

        # Wait for background update check
        self.assertTrue(is_running('__workflow_update_check'))
        while is_running('__workflow_update_check'):
            time.sleep(0.05)

        # Remote version is same as the one we passed to Workflow
        self.assertFalse(wf.update_available)
        self.assertFalse(wf.start_update())

        wf.reset()

        # Initialise with outdated version allowing prerelease updates
        wf = Workflow(update_settings={
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': 'v2.0',
            'prereleases': True,
            'frequency': 1,
        })

        wf.run(fake)

        # Check won't have completed yet
        self.assertFalse(wf.update_available)

        # wait for background update check
        self.assertTrue(is_running('__workflow_update_check'))
        while is_running('__workflow_update_check'):
            time.sleep(0.05)
        time.sleep(1)

        # There *is* a newer version in the repo
        self.assertTrue(wf.update_available)

        # Mock out subprocess and check the correct command is run
        c = WorkflowMock()
        with c:
            self.assertTrue(wf.start_update())
        # wf.logger.debug('start_update : {}'.format(c.cmd))
        self.assertEquals(c.cmd[0], '/usr/bin/python')
        self.assertEquals(c.cmd[2], '__workflow_update_install')

        # Grab the updated release data, then reset the cache
        update_info = wf.cached_data('__workflow_update_status')

        wf.reset()

        # Initialise with latest available prerelease
        wf = Workflow(update_settings={
            'github_slug': 'deanishe/alfred-workflow-dummy',
            'version': update_info['version'],
            'prereleases': True
        })

        wf.run(fake)

        # Wait for background update check
        self.assertTrue(is_running('__workflow_update_check'))
        while is_running('__workflow_update_check'):
            time.sleep(0.05)

        # Remote version is same as the one we passed to Workflow
        self.assertFalse(wf.update_available)
        self.assertFalse(wf.start_update())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
