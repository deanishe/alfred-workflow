# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created 2019-05-05

"""Unit tests for sys.path manipulation."""



import os
import sys

import pytest

from workflow.workflow import Workflow


LIBS = [os.path.join(os.path.dirname(__file__), 'lib')]


def test_additional_libs(alfred4, infopl):
    """Additional libraries"""
    wf = Workflow(libraries=LIBS)
    for path in LIBS:
        assert path in sys.path

    assert sys.path[0:len(LIBS)] == LIBS
    import youcanimportme
    youcanimportme.noop()
    wf.reset()


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
