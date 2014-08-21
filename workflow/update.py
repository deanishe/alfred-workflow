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
...
wf = Workflow(update_info={
    'github_slug': 'username/reponame',  # GitHub slug
    'version': 'v1.0',  # Version number
    'frequency': 7, # Optional
})
...
if wf.update_available:
    wf.start_update()

:param force: Force an update check
:type force: ``Boolean``
"""

from __future__ import print_function, unicode_literals

import os
import tempfile
import argparse

import workflow
from web import get

__all__ = ['']

wf = workflow.Workflow()
log = wf.logger

RELEASES_BASE = 'https://api.github.com/repos/%s/releases'

def _download_workflow(github_url):
    filename = github_url.split("/")[-1]
    if (not github_url.endswith('.alfredworkflow') or
            not filename.endswith('.alfredworkflow')):
        raise ValueError('Attachment %s not a workflow' % filename)
    local_file = os.path.join(tempfile.gettempdir(), filename)
    response = get(github_url)
    with open(local_file, 'wb') as output:
        output.write(response.content)
    return local_file

def _get_api_url(slug):
    if len(slug.split('/')) != 2:
        raise ValueError('Invalid GitHub slug : %s' % slug)
    return RELEASES_BASE % slug

def _extract_info(releases):
    if len(releases) < 1:
        raise IndexError('No release found')
    latest_release = releases[0]
    if 'tag_name' not in latest_release:
        raise KeyError('No version found')
    download_url = _extract_download_url(latest_release)
    return (latest_release['tag_name'], download_url)

def _extract_download_url(release):
    if ('assets' not in release or
            len(release['assets']) != 1 or
            'browser_download_url' not in release['assets'][0]):
        raise KeyError('No attachment found')
    return release['assets'][0]['browser_download_url']

def _check_update(github_slug, current_version):
    releases = get(_get_api_url(github_slug)).json()
    (latest_version, download_url) = _extract_info(releases)
    if current_version == latest_version:
        wf.cache_data('__workflow_update_available', {
            'available': False
        })
        return False
    wf.cache_data('__workflow_update_available', {
        'version': latest_version,
        'download_url': download_url,
        'available': True
    })
    return True

if __name__ == '__main__':  # pragma: nocover
    parser = argparse.ArgumentParser()
    parser.add_argument("github_slug", help="")
    parser.add_argument("version", help="")
    args = parser.parse_args()
    _check_update(args.github_slug, args.version)
    