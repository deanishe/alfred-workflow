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

import urllib
import tempfile
import re
import argparse

import workflow
from web import get

__all__ = ['']

wf = workflow.Workflow()
log = wf.logger

DEFAULT_FREQUENCY = 1
RELEASES_BASE = 'https://api.github.com/repos/%s/releases'
COMPONENT_RE = re.compile(r'(\d+ | [a-z]+ | \.| -)', re.VERBOSE)

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

def _get_api_url(slug):
    if len(slug.split('/')) != 2:
        raise ValueError('Invalid GitHub slug : %s' % slug)
    return RELEASES_BASE % slug

def _extract_version(release):
    if 'tag_name' not in release:
        raise RuntimeError('No version found')
    return release['tag_name']

def _parse_version_parts(s):
    for part in COMPONENT_RE.split(s):
        if not part or part=='.':
            continue
        if part[:1] in '0123456789':
            yield int(part)
        else:
            yield part
    yield ''

def _parse_version(s):
    parts = []
    for part in _parse_version_parts(s.lower()):
        if part is not '':
            parts.append(part)
    return tuple(parts)

def _is_latest(local, remote):
    local = _parse_version(local)
    remote = _parse_version(remote)
    if len(local) != len(remote):
        return False
    for i in range(len(local)):
        if (isinstance(local[i], int) and
                isinstance(remote[i], int)):
            if local[i] < remote[i]:
                return False
            elif local[i] > remote[i]:
                return True
        else:
            if local[i] != remote[i]:
                return False
    return True

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

def _update_available(github_slug, current_version):
    release_list = get(_get_api_url(github_slug)).json()
    latest_release = _get_latest_release(release_list)
    latest_version = _extract_version(latest_release)
    if _is_latest(current_version, latest_version):
        wf.cache_data('__workflow_update_available', {
            'available': False
        })
        return False
    wf.cache_data('__workflow_update_available', {
        'version': latest_version,
        'download_url': _extract_download_url(latest_release),
        'available': True
    })
    return True

def main(github_slug, version, frequency):
    if not wf.cached_data_fresh('__workflow_update_available', frequency * 86400):
        _update_available(github_slug, version)

if __name__ == '__main__':  # pragma: nocover
    parser = argparse.ArgumentParser()
    parser.add_argument("github_slug", help="")
    parser.add_argument("version", help="")
    parser.add_argument("-f", "--frequency", type=int, help="")
    args = parser.parse_args()
    frequency = args.frequency if args.frequency else DEFAULT_FREQUENCY
    main(args.github_slug, args.version, frequency)
    