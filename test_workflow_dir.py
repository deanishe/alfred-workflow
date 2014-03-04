#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8
"""
test_workflow_dir.py

This test can't be included in the main test library, as it requires
no `info.plist` to be present in order to function (i.e. fail)

Created by deanishe@deanishe.net on 2014-03-04.
Copyright (c) 2014 deanishe@deanishe.net

MIT Licence. See http://opensource.org/licenses/MIT

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
