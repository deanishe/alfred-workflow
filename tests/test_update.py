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

from workflow import Workflow
import workflow.update as u


class UpdateTests(unittest.TestCase):

    def setUp(self):
        self.wf = Workflow()

    def test_download_workflow(self):
        """Update: Download workflow update"""
        self.assertRaises(ValueError, u._download_workflow, 'http://github.com/file.zip')
        local_file = u._download_workflow('https://github.com/fniephaus/alfred-pocket/releases/download/v2.1/Pocket-for-Alfred.alfredworkflow')
        self.assertTrue(local_file.endswith('.alfredworkflow'))
        self.assertTrue(os.path.isfile(local_file))

    def test_get_api_url(self):
        """Update: Get API URL"""
        url = u._get_api_url('fniephaus/alfred-workflow')
        expected = 'https://api.github.com/repos/fniephaus/alfred-workflow/releases'
        self.assertEquals(url, expected)
        self.assertRaises(ValueError, u._get_api_url, 'fniephausalfred-workflow')

    def test_extract_info(self):
        """Update: Extract release info"""
        releases = [{
            'tag_name': 'v1.2',
            'assets': [{
                'browser_download_url': 'https://github.com/'
            }]
        }]
        (version, url) = u._extract_info(releases)
        self.assertEquals(version, 'v1.2')
        self.assertEquals(url, 'https://github.com/')
        self.assertRaises(IndexError, u._extract_info, [])
        del releases[0]['assets']
        self.assertRaises(KeyError, u._extract_info, releases)
        del releases[0]['tag_name']
        self.assertRaises(KeyError, u._extract_info, releases)

    def test_check_update(self):
        """Update: Check update"""
        self.assertTrue(u._check_update('fniephaus/alfred-pocket', 'v0.0'))
        update_info = self.wf.cached_data('__workflow_update_available')
        self.assertFalse(u._check_update('fniephaus/alfred-pocket', update_info['version']))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
