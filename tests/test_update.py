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
Test self update capabilities
"""

from __future__ import print_function

import unittest

from workflow import Workflow
import workflow.update as u


class UpdateTests(unittest.TestCase):

    def setUp(self):
        self.wf = Workflow()

    def test_update(self):
        """Update: Test self update"""
        self.assertRaises(ValueError, u.update, {'frequency': 1})
        slug = 'fniephaus/alfred-pocket'
        version = 'v999.9'
        frequency = 8
        u.update({
            'github_slug': slug,  # GitHub slug
            'version': version,  # Version number
            'auto': True,
            'frequency': frequency, # Optional
        }, force=True)
        self.assertEquals(self.wf.settings['__update_github_slug'], slug)
        self.assertEquals(self.wf.settings['__update_version'], version)
        self.assertEquals(self.wf.settings['__update_frequency'], frequency)

    def test_download_workflow(self):
        """Update: Bad attachment"""
        self.assertRaises(RuntimeError, u._download_workflow, 'http://github.com/test.zip')

    def test_frequency(self):
        """Update: Frequency"""
        u.wf.settings['__update_frequency'] = None
        self.assertEquals(u._frequency(), u.DEFAULT_FREQUENCY * 60 * 60 * 24)
        u.wf.settings['__update_frequency'] = 14
        self.assertEquals(u._frequency(), 14 * 60 * 60 * 24)

    def test_get_api_url(self):
        """Update: Get API URL"""
        url = u._get_api_url('fniephaus/alfred-workflow')
        expected = 'https://api.github.com/repos/fniephaus/alfred-workflow/releases'
        self.assertEquals(url, expected)
        self.assertRaises(ValueError, u._get_api_url, 'fniephausalfred-workflow')

    def test_extract_version(self):
        """Update: Extract version"""
        version = u._extract_version({'tag_name': 'v1.0'})
        expected = 'v1.0'
        self.assertEquals(version, expected)
        self.assertRaises(RuntimeError, u._extract_version, {})

    def test_extract_download_url(self):
        """Update: Extract download URL"""
        url = u._extract_download_url({'assets': [{'browser_download_url': 'http://github.com/'}]})
        expected = 'http://github.com/'
        self.assertEquals(url, expected)
        self.assertRaises(RuntimeError, u._extract_download_url, {})

    def test_get_latest_release(self):
        """Update: Extract download URL"""
        release_list = u._get_latest_release([1, 2, 3])
        self.assertEquals(release_list, 1)
        self.assertRaises(RuntimeError, u._get_latest_release, [])

    def test_update_available(self):
        """Update: update available"""
        u.wf.clear_settings()
        u.wf = Workflow()
        self.assertRaises(ValueError, u._update_available)
        self.assertFalse(u.update_available())
        u.wf.clear_settings()
        u.wf = Workflow()
        u.update({
            'github_slug': 'fniephaus/alfred-pocket',
            'version': 'v0.0'
        })
        self.assertTrue(u._update_available())
        self.assertTrue(u.update_available())
        u.wf.clear_settings()
        u.wf = Workflow()
        u.wf.settings['__update_github_slug'] = 'fniephaus/alfred-pocket'
        u.wf.settings['__update_version'] = 'v999.9'
        self.assertFalse(u._update_available())
        self.assertFalse(u.update_available())

    def test_initiate_update_fail(self):
        """Update: Don't initialize update if none available"""
        u.wf.settings['__update_github_slug'] = 'fniephaus/alfred-pocket'
        u.wf.settings['__update_version'] = 'v999.9'
        self.assertFalse(u._initiate_update())

    def test_main(self):
        """Update: Main function"""
        u.wf.clear_settings()
        u.wf = Workflow()
        u.wf.settings['__update_github_slug'] = 'fniephaus/alfred-pocket'
        u.wf.settings['__update_version'] = 'v999.9'
        self.assertFalse(u.main(self.wf))
        u.wf.clear_cache()
        u.wf.settings['__update_auto'] = True
        u.wf.settings['__update_version'] = 'v0.0'
        self.assertTrue(u.main(self.wf))
        self.assertFalse(u.main(self.wf))
        u.wf.clear_cache()
        u.wf.settings['__update_auto'] = False
        u.wf.settings['__update_version'] = 'v0.0'
        self.assertTrue(u.main(self.wf))
        self.assertFalse(u.main(self.wf))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
