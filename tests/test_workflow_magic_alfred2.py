# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created on 2019-05-05

"""Unit tests for Alfred 2 magic argument handling."""



import pytest

from workflow import Workflow

from .conftest import env
from .util import VersionFile, WorkflowMock


def test_version_magic(infopl2):
    """Magic: version magic (Alfred 2)"""
    vstr = '1.9.7'
    # Version from version file
    with env(alfred_workflow_version=None):
        # Versioned
        with WorkflowMock(['script', 'workflow:version']) as c:
            with VersionFile(vstr):
                wf = Workflow()
                # Process magic arguments
                wf.args
                assert not c.cmd
                wf.reset()

        # Unversioned
        with WorkflowMock(['script', 'workflow:version']) as c:
            wf = Workflow()
            # Process magic arguments
            wf.args
            assert not c.cmd
            wf.reset()

    # Version from environment variable
    with env(alfred_workflow_version=vstr):
        with WorkflowMock(['script', 'workflow:version']) as c:
            wf = Workflow()
            # Process magic arguments
            wf.args
            assert not c.cmd
            wf.reset()


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
