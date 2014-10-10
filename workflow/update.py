#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 Fabio Niephaus <fabio.niephaus@gmail.com>,
# Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#

"""
Self-updating from GitHub

.. versionadded:: 1.9

.. note::

   This module is not intended to be used directly. Automatic updates
   are controlled by the ``update_settings`` :class:`dict` passed to
   :class:`~workflow.workflow.Workflow` objects.

"""

from __future__ import print_function, unicode_literals

import os
import tempfile
import argparse
import re
import subprocess

import workflow
import web

prefixed_version = re.compile(r'^v\d+.*', re.IGNORECASE).match

# __all__ = []

wf = workflow.Workflow()
log = wf.logger

RELEASES_BASE = 'https://api.github.com/repos/{}/releases'


def download_workflow(url):
    """Download workflow at ``url`` to a local temporary file

    :param url: URL to .alfredworkflow file in GitHub repo
    :returns: path to downloaded file

    """

    filename = url.split("/")[-1]

    if (not url.endswith('.alfredworkflow') or
            not filename.endswith('.alfredworkflow')):
        raise ValueError('Attachment `{}` not a workflow'.format(filename))

    local_path = os.path.join(tempfile.gettempdir(), filename)

    log.debug('Downloading updated workflow from `{}` to `{}` ...'.format(url,
              local_path))

    response = web.get(url)

    with open(local_path, 'wb') as output:
        output.write(response.content)

    return local_path


def build_api_url(slug):
    """Generate releases URL from GitHub slug

    :param slug: Repo name in form ``username/repo``
    :returns: URL to the API endpoint for the repo's releases

     """

    if len(slug.split('/')) != 2:
        raise ValueError('Invalid GitHub slug : {}'.format(slug))

    return RELEASES_BASE.format(slug)


def get_valid_releases(github_slug):
    """Return list of all valid releases

    :param github_slug: ``username/repo`` for workflow's GitHub repo
    :returns: list of dicts. Each :class:`dict` has the form
        ``{'version': '1.1', 'download_url': 'http://github...'}


    A valid release is one that contains one ``.alfredworkflow`` file.

    If the GitHub version (i.e. tag) is of the form ``v1.1``, the leading
    ``v`` will be stripped.

    """

    api_url = build_api_url(github_slug)
    releases = []

    log.debug('Retrieving releases list from `{}` ...'.format(api_url))

    def retrieve_releases():
        log.info('Retriving releases for `{}` ...'.format(github_slug))
        return web.get(api_url).json()

    slug = github_slug.replace('/', '-')
    for release in wf.cached_data('gh-releases-{}'.format(slug),
                                  retrieve_releases):
        version = release['tag_name']
        download_urls = []
        for asset in release.get('assets', []):
            url = asset.get('browser_download_url')
            if not url or not url.endswith('.alfredworkflow'):
                continue
            download_urls.append(url)

        # Validate release
        if release['prerelease']:
            log.warning(
                'Invalid release {} : pre-release detected'.format(version))
            continue
        if not download_urls:
            log.warning(
                'Invalid release {} : No workflow file'.format(version))
            continue
        if len(download_urls) > 1:
            log.warning(
                'Invalid release {} : multiple workflow files'.format(version))
            continue

        # Normalise version
        if prefixed_version(version):
            version = version[1:]

        log.debug('Release `{}` : {}'.format(version, url))
        releases.append({'version': version, 'download_url': download_urls[0]})

    return releases


def is_newer_version(local, remote):
    """Return ``True`` if ``remote`` version is newer than ``local``

    :param local: version of installed workflow
    :param remote: version of remote workflow
    :returns: ``True`` or ``False``

    """

    local = local.lower()
    remote = remote.lower()

    if prefixed_version(local):
        local = local[1:]

    if prefixed_version(remote):
        remote = remote[1:]

    is_newer = remote != local

    log.debug('remote `{}` newer that local `{}` : {}'.format(
              remote, local, is_newer))

    return is_newer


def check_update(github_slug, current_version):
    """Check whether a newer release is available on GitHub

    :param github_slug: ``username/repo`` for workflow's GitHub repo
    :param current_version: the currently installed version of the
        workflow. This should be a string.
        `Semantic versioning <http://semver.org>`_ is *very strongly*
        recommended.
    :returns: ``True`` if an update is available, else ``False``

    If an update is available, its version number and download URL will
    be cached.

    """

    releases = get_valid_releases(github_slug)

    log.info('{} releases for {}'.format(len(releases), github_slug))

    if not len(releases):
        raise ValueError('No valid releases for {}'.format(github_slug))

    # GitHub returns releases newest-first
    latest_release = releases[0]

    # (latest_version, download_url) = get_latest_release(releases)
    if is_newer_version(current_version, latest_release['version']):

        wf.cache_data('__workflow_update_status', {
            'version': latest_release['version'],
            'download_url': latest_release['download_url'],
            'available': True
        })

        return True

    wf.cache_data('__workflow_update_status', {
        'available': False
    })
    return False


def install_update(github_slug, current_version):
    """If a newer release is available, download and install it

    :param github_slug: ``username/repo`` for workflow's GitHub repo
    :param current_version: the currently installed version of the
        workflow. This should be a string.
        `Semantic versioning <http://semver.org>`_ is *very strongly*
        recommended.

    If an update is available, it will be downloaded and installed.

    :returns: ``True`` if an update is installed, else ``False``

    """

    update_data = wf.cached_data('__workflow_update_status', max_age=0)

    if not update_data or not update_data.get('available'):
        wf.logger.info('No update available')
        return False

    local_file = download_workflow(update_data['download_url'])

    wf.logger.info('Installing updated workflow ...')
    subprocess.call(['open', local_file])

    update_data['available'] = False
    wf.cache_data('__workflow_update_status', update_data)
    return True


if __name__ == '__main__':  # pragma: nocover
    parser = argparse.ArgumentParser(
        description='Check for and install updates')
    parser.add_argument(
        'action',
        choices=['check', 'install'],
        help='Check for new version or install new version?')
    parser.add_argument(
        'github_slug',
        help='GitHub repo name in format "username/repo"')
    parser.add_argument(
        'version',
        help='The version of the installed workflow')

    args = parser.parse_args()
    if args.action == 'check':
        check_update(args.github_slug, args.version)
    elif args.action == 'install':
        install_update(args.github_slug, args.version)
