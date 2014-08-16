#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>, Fabio Niephaus <fabio.niephaus@gmail.com>
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

from workflow import Workflow


class UpdateTests(unittest.TestCase):

    def test_disabled(self):
        wf = Workflow()
        self.assertFalse(wf.auto_update())
        wf.reset()

    def test_bad_github_slug(self):
        wf = Workflow(default_settings={
            'auto_update_github': 'fniephausalfred-pocket',
            'auto_update_version': 'v0.0',
        }, autoupdate=False)
        self.assertFalse(wf.auto_update())
        wf.reset()

    def test_no_workflow_attachment(self):
        wf = Workflow(default_settings={
            'auto_update_github': 'deanishe/alfred-workflow',
            'auto_update_version': 'v0.0',
        }, autoupdate=False)
        self.assertFalse(wf.auto_update())
        wf.reset()

    def test_no_releases(self):
        wf = Workflow(default_settings={
            'auto_update_github': 'django/django',
            'auto_update_version': 'v0.0',
        }, autoupdate=False)
        self.assertFalse(wf.auto_update())
        wf.reset()

    def test_up_to_date(self):
        wf = Workflow(default_settings={
            'auto_update_github': 'fniephaus/alfred-pocket',
            'auto_update_version': 'v999.9',
            'auto_update_frequency': 14,
        })
        self.assertFalse(wf.auto_update())
        wf.reset()

    def test_update(self):
        wf = Workflow(default_settings={
            'auto_update_github': 'fniephaus/alfred-pocket',
            'auto_update_version': 'v0.0',
        }, autoupdate=False)
        self.assertTrue(wf.auto_update())
        self.assertFalse(wf.auto_update())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
