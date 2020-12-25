# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created 2019-05-05

"""Unit tests for serializers."""



import pytest


def test_unicode_paths(wf):
    """Workflow paths are Unicode"""
    s = 'test.txt'
    u = 'über.txt'
    assert isinstance(wf.datadir, str)
    assert isinstance(wf.datafile(s), str)
    assert isinstance(wf.datafile(u), str)
    assert isinstance(wf.cachedir, str)
    assert isinstance(wf.cachefile(s), str)
    assert isinstance(wf.cachefile(u), str)
    assert isinstance(wf.workflowdir, str)
    assert isinstance(wf.workflowfile(s), str)
    assert isinstance(wf.workflowfile(u), str)


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
