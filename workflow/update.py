#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 Fabio Niephaus <fabio.niephaus@gmail.com>, Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#

"""
Enables self-updating capabilities for a workflow. It regularly (7 days
by default) fetches the latest releases from a given GitHub repository
and then asks the user to replace the workflow if a newer version is
available.

This feature requires default settings to be set like this:


from workflow import Workflow
from workflow.update import auto_update
...
wf = Workflow()
...
auto_update({
    'github_slug': 'username/reponame',  # GitHub slug
    'version': 'v1.0',  # Version number
    'frequency': 7, # Optional
})

:param config: Auto update configuration
:type config: ``dict``
:param force: Force an update check
:type force: ``Boolean``
:rtype: ``Boolean``

"""

from __future__ import print_function, unicode_literals

import os
import urllib
import tempfile
from pkg_resources import parse_version

from workflow import Workflow
from background import is_running, run_in_background
from web import get

__all__ = ['auto_update']

wf = Workflow()
log = wf.logger

DEFAULT_FREQUENCY = 7
RELEASES_BASE = 'https://api.github.com/repos/%s/releases'


def auto_update(config, force=False):
    try:
        wf.settings['__update_github_slug'] = config['github_slug']
        wf.settings['__update_version'] = config['version']
    except KeyError:
        raise ValueError('Auto update settings incorrect')
    if 'frequency' in config:
        wf.settings['__update_frequency'] = config['frequency']
    if force:
        wf.cache_data('auto_update', None)
    if not is_running('auto_update'):
        cmd = ['/usr/bin/python', wf.workflowfile('workflow/update.py')]
        run_in_background('auto_update', cmd)

def _download_workflow(github_url):
    filename = github_url.split("/")[-1]
    if (not github_url.endswith('.alfredworkflow') or
            not filename.endswith('.alfredworkflow')):
        raise RuntimeError('Attachment %s not a workflow' % filename)
    download_url = get(github_url).url # resolve redirect
    file_downloader = urllib.URLopener()
    local_file = '%s/%s' % (tempfile.gettempdir(), filename)
    file_downloader.retrieve(download_url, local_file)
    return local_file

def _frequency():
    frequency = None
    if 'auto_update_frequency' in wf.settings:
        frequency = wf.settings['__update_frequency']
    if isinstance(frequency, int):
        return frequency * 86400
    else:
        return DEFAULT_FREQUENCY * 86400

def _get_api_url(slug):
    if len(slug.split('/')) != 2:
        raise ValueError('Invalid GitHub slug : %s' % slug)
    return RELEASES_BASE % slug

def _extract_version(release):
    if 'tag_name' not in release:
        raise RuntimeError('No version found')
    return release['tag_name']

def _is_latest(current_version, latest_version):
    return parse_version(current_version) >= parse_version(latest_version)

def _extract_download_url(release):
    if ('assets' not in release or
            len(release['assets']) != 1 or
            'browser_download_url' not in release['assets'][0]):
        raise RuntimeError('No attachment found')
    return release['assets'][0]['browser_download_url']

def _get_latest_release(release_list):
    if len(release_list) < 1:
        raise RuntimeError('No release found')
    return release_list[0]
def main(wf):
    github_slug = wf.settings['__update_github_slug']
    current_version = wf.settings['__update_version']
    if wf.cached_data_fresh('auto_update', _frequency()):
        return False
    release_list = get(_get_api_url(github_slug)).json()
    latest_release = _get_latest_release(release_list)
    latest_version = _extract_version(latest_release)
    if _is_latest(current_version, latest_version):
        return False
    download_url = _extract_download_url(latest_release)
    local_file = _download_workflow(download_url)
    wf.cache_data('auto_update', True)
    os.system('open "%s"' % local_file)
    wf.logger.debug('Update initiated')
    return True

if __name__ == '__main__':  # pragma: no cover
    wf.run(main)
    