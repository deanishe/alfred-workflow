#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-04
#
"""

Ensure Workflow fails if there is no ``info.plist``.

"""

from __future__ import print_function

import os
import unittest

from workflow import Workflow

INFO_PLIST = os.path.join(os.path.dirname(__file__), 'info.plist')
TEMP_PATH = INFO_PLIST + '.temp'


class WorkflowDirTests(unittest.TestCase):

    def setUp(self):
        if os.path.exists(INFO_PLIST):
            os.rename(INFO_PLIST, TEMP_PATH)

    def tearDown(self):
        if os.path.exists(TEMP_PATH):
            os.rename(TEMP_PATH, INFO_PLIST)

    def test_workflowdir(self):
        """workflowdir fails"""
        with self.assertRaises(IOError):
            wf = Workflow()
            wf.workflowdir


if __name__ == '__main__':
    unittest.main()
