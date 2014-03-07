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
test_workflow_dir.py

This test can't be included in the main test library, as it requires
no `info.plist` to be present in order to function (i.e. fail)

"""

from __future__ import print_function

import unittest

from workflow import Workflow


class WorkflowDirTests(unittest.TestCase):

    def test_workflowdir(self):
        """workflowdir fails"""
        with self.assertRaises(IOError):
            wf = Workflow()
            wf.workflowdir


if __name__ == '__main__':
    unittest.main()
