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
    'auto': False, # Start update process automatically
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

from workflow import Workflow
from background import is_running, run_in_background
from web import get

__all__ = ['update', 'update_available']

wf = Workflow()
log = wf.logger

DEFAULT_FREQUENCY = 7
RELEASES_BASE = 'https://api.github.com/repos/%s/releases'


def update(config, force=False):
    try:
        wf.settings['__update_github_slug'] = config['github_slug']
        wf.settings['__update_version'] = config['version']
    except KeyError:
        raise ValueError('Auto update settings incorrect')
    if 'auto' in config:
        wf.settings['__update_auto'] = config['auto']
    if 'frequency' in config:
        wf.settings['__update_frequency'] = config['frequency']
    if force:
        wf.cache_data('__update', None)
    if not is_running('__update'):
        cmd = ['/usr/bin/python', wf.workflowfile('workflow/update.py')]
        run_in_background('__update', cmd)

def update_available():
    update_data = wf.cached_data('__update')
    if (update_data is None or
        'available' not in update_data):
        return False
    return update_data['available']

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
    if '__update_frequency' in wf.settings:
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

def _update_available():
    try:
        github_slug = wf.settings['__update_github_slug']
        current_version = wf.settings['__update_version']
    except KeyError:
        raise ValueError('Auto update settings incorrect')
    release_list = get(_get_api_url(github_slug)).json()
    latest_release = _get_latest_release(release_list)
    latest_version = _extract_version(latest_release)
    if current_version == latest_version:
        wf.cache_data('__update', {
            'available': False
        })
        return False
    wf.cache_data('__update', {
        'version': latest_version,
        'download_url': _extract_download_url(latest_release),
        'available': True
    })
    return True

def _initiate_update():
    _update_available()
    update_data = wf.cached_data('__update')
    if (update_data is None or
        'download_url' not in update_data):
        return False
    local_file = _download_workflow(update_data['download_url'])
    wf.cache_data('__update', True)
    os.system('open "%s"' % local_file)
    wf.logger.debug('Update initiated')
    return True

def main(workflow):
    if wf.cached_data_fresh('__update', _frequency()):
        return False
    if ('__update_auto' in wf.settings and 
            wf.settings['__update_auto'] == True):
        return _initiate_update()
    else:
        return _update_available()

if __name__ == '__main__':  # pragma: nocover
    wf.run(main)
    