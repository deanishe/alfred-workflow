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
Test auto update capabilities
"""

from __future__ import print_function

import unittest
from pkg_resources import parse_version

from workflow import Workflow
import workflow.update as update


class UpdateTests(unittest.TestCase):

    def setUp(self):
        self.wf = Workflow()

    def test_auto_update(self):
        """Test auto update"""
        self.assertRaises(ValueError, update.auto_update, {'frequency': 1})
        slug = 'fniephaus/alfred-pocket'
        version = 'v999.9'
        frequency = 8
        update.auto_update({
            'github_slug': slug,  # GitHub slug
            'version': version,  # Version number
            'frequency': frequency, # Optional
        }, force=True)
        self.assertEquals(self.wf.settings['__update_github_slug'], slug)
        self.assertEquals(self.wf.settings['__update_version'], version)
        self.assertEquals(self.wf.settings['__update_frequency'], frequency)

    def test_download_workflow(self):
        """Update: Bad attachment"""
        self.assertRaises(RuntimeError, update._download_workflow, 'http://github.com/test.zip')

    def test_frequency(self):
        """Update: Frequency"""
        update.wf.settings['__update_frequency'] = None
        self.assertEquals(update._frequency(), update.DEFAULT_FREQUENCY * 60 * 60 * 24)
        update.wf.settings['__update_frequency'] = 14
        self.assertEquals(update._frequency(), 14 * 60 * 60 * 24)

    def test_get_api_url(self):
        """Update: Get API URL"""
        url = update._get_api_url('fniephaus/alfred-workflow')
        expected = 'https://api.github.com/repos/fniephaus/alfred-workflow/releases'
        self.assertEquals(url, expected)
        self.assertRaises(ValueError, update._get_api_url, 'fniephausalfred-workflow')

    def test_extract_version(self):
        """Update: Extract version"""
        version = update._extract_version({'tag_name': 'v1.0'})
        expected = 'v1.0'
        self.assertEquals(version, expected)
        self.assertRaises(RuntimeError, update._extract_version, {})

    def test_is_latest(self):
        """Update: Is latest"""
        self.assertTrue(update._is_latest('v1.0', 'v1.0'))
        self.assertTrue(update._is_latest('v1.0', 'v0.9'))
        self.assertTrue(update._is_latest('v2.10', 'v2.9'))
        self.assertFalse(update._is_latest('v0.9', 'v1.0'))
        self.assertFalse(update._is_latest('v1.9', 'v1.10'))
        self.assertFalse(update._is_latest('v99.100', 'v100'))

    def test_extract_download_url(self):
        """Update: Extract download URL"""
        url = update._extract_download_url({'assets': [{'browser_download_url': 'http://github.com/'}]})
        expected = 'http://github.com/'
        self.assertEquals(url, expected)
        self.assertRaises(RuntimeError, update._extract_download_url, {})

    def test_get_latest_release(self):
        """Update: Extract download URL"""
        release_list = update._get_latest_release([1, 2, 3])
        self.assertEquals(release_list, 1)
        self.assertRaises(RuntimeError, update._get_latest_release, [])

    def test_main(self):
        """Update: Main function"""
        self.wf.settings['__update_version'] = 'v999.9'
        self.assertFalse(update.main(self.wf))
        self.wf.clear_cache()
        self.wf.settings['__update_version'] = 'v0.0'
        self.assertTrue(update.main(self.wf))
        self.assertFalse(update.main(self.wf))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
