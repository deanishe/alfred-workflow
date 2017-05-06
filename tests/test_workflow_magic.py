#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-05-06
#

"""
"""

from __future__ import print_function

import os

import pytest

from workflow import Workflow

from util import VersionFile, WorkflowMock


def test_list_magic(info2):
    """Magic: list magic"""
    # TODO: Verify output somehow
    with WorkflowMock(['script', 'workflow:magic']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert not c.cmd


def test_version_magic(info2):
    """Magic: version magic"""
    # TODO: Verify output somehow

    vstr = '1.9.7'

    # Versioned
    with WorkflowMock(['script', 'workflow:version']) as c:
        with VersionFile(vstr):
            wf = Workflow()
            # Process magic arguments
            wf.args

        assert not c.cmd
        # wf.logger.debug('STDERR : {0}'.format(c.stderr))

    # Unversioned
    with WorkflowMock(['script', 'workflow:version']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert not c.cmd


def test_openhelp(info2):
    """Magic: open help URL"""
    url = 'http://www.deanishe.net/alfred-workflow/'
    with WorkflowMock(['script', 'workflow:help']) as c:
        wf = Workflow(help_url=url)
        # Process magic arguments
        wf.args
        assert c.cmd == ['open', url]


def test_openhelp_no_url(info2):
    """Magic: no help URL"""
    with WorkflowMock(['script', 'workflow:help']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert not c.cmd


def test_openlog(info2):
    """Magic: open logfile"""
    with WorkflowMock(['script', 'workflow:openlog']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert c.cmd == ['open', wf.logfile]


def test_cachedir(info2):
    """Magic: open cachedir"""
    with WorkflowMock(['script', 'workflow:opencache']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert c.cmd == ['open', wf.cachedir]


def test_datadir(info2):
    """Magic: open datadir"""
    with WorkflowMock(['script', 'workflow:opendata']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert c.cmd == ['open', wf.datadir]


def test_workflowdir(info2):
    """Magic: open workflowdir"""
    with WorkflowMock(['script', 'workflow:openworkflow']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert c.cmd == ['open', wf.workflowdir]


def test_open_term(info2):
    """Magic: open Terminal"""
    with WorkflowMock(['script', 'workflow:openterm']) as c:
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert c.cmd == ['open', '-a', 'Terminal', wf.workflowdir]


def test_delete_data(info2):
    """Magic: delete data"""
    with WorkflowMock(['script', 'workflow:deldata']):
        wf = Workflow()
        testpath = wf.datafile('file.test')
        with open(testpath, 'wb') as fp:
            fp.write('test!')

        assert os.path.exists(testpath)
        # Process magic arguments
        wf.args
        assert not os.path.exists(testpath)


def test_delete_cache(info2):
    """Magic: delete cache"""
    with WorkflowMock(['script', 'workflow:delcache']):
        wf = Workflow()
        testpath = wf.cachefile('file.test')
        with open(testpath, 'wb') as fp:
            fp.write('test!')

        assert os.path.exists(testpath)
        # Process magic arguments
        wf.args
        assert not os.path.exists(testpath)


def test_reset(info2):
    """Magic: reset"""
    with WorkflowMock(['script', 'workflow:reset']):
        wf = Workflow()
        wf.settings['key'] = 'value'
        datatest = wf.datafile('data.test')
        cachetest = wf.cachefile('cache.test')
        settings_path = wf.datafile('settings.json')

        for p in (datatest, cachetest):
            with open(p, 'wb') as file_obj:
                file_obj.write('test!')

        for p in (datatest, cachetest, settings_path):
            assert os.path.exists(p)

        # Process magic arguments
        wf.args

        for p in (datatest, cachetest, settings_path):
            assert not os.path.exists(p)


def test_delete_settings(info2):
    """Magic: delete settings"""
    with WorkflowMock(['script', 'workflow:delsettings']):
        wf = Workflow()
        wf.settings['key'] = 'value'

        assert os.path.exists(wf.settings_path)

        wf2 = Workflow()
        assert wf2.settings['key'] == 'value'

        # Process magic arguments
        wf.args

        wf3 = Workflow()
        assert 'key' not in wf3.settings


def test_folding(info2):
    """Magic: folding"""
    with WorkflowMock(['script', 'workflow:foldingdefault']):
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_diacritic_folding') is None

    with WorkflowMock(['script', 'workflow:foldingon']):
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_diacritic_folding') is True

    with WorkflowMock(['script', 'workflow:foldingdefault']):
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_diacritic_folding') is None

    with WorkflowMock(['script', 'workflow:foldingoff']):
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_diacritic_folding') is False


def test_prereleases(info2):
    """Magic: prereleases"""
    with WorkflowMock(['script', 'workflow:prereleases']):
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_prereleases') is True
        assert wf.prereleases is True

    with WorkflowMock(['script', 'workflow:noprereleases']):
        wf = Workflow()
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_prereleases') is False
        assert wf.prereleases is False


def test_update_settings_override_magic_prereleases(info2):
    """Magic: pre-release updates can be overridden by `True` value for `prereleases` key in `update_settings`"""
    with WorkflowMock(['script', 'workflow:prereleases']):
        d = {'prereleases': True}
        wf = Workflow(update_settings=d)
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_prereleases') is True
        assert wf.prereleases is True

    with WorkflowMock(['script', 'workflow:noprereleases']):
        wf = Workflow(update_settings=d)
        # Process magic arguments
        wf.args
        assert wf.settings.get('__workflow_prereleases') is False
        assert wf.prereleases is True


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
