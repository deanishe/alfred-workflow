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

from __future__ import print_function, unicode_literals, absolute_import

import os
import tempfile
import subprocess

from workflow import base, hooks, web, workflow

# __all__ = []

log = base.get_logger(__name__)

RELEASES_BASE = 'https://api.github.com/repos/{0}/releases'

ONE_HOUR = 3600
ONE_DAY = ONE_HOUR * 24
ONE_WEEK = ONE_DAY * 7

_wf = None


def wf():
    global _wf
    if _wf is None:
        _wf = workflow.Workflow()
    return _wf


class Updater(object):
    """Base class for auto-updaters

    Subclasses must override the following methods:

    - :meth:`get_updater`
    - :meth:`get_latest_version_info`

    """

    @staticmethod
    def get_updater(update_settings):
        """Return :class:`Updater` instance for ``update_settings``"""
        raise NotImplementedError()

    def __init__(self, update_settings):
        self.settings = update_settings

    def get_latest_version_info(self):
        """Check web/filesystem/whatever for new version

        :returns: :class:`Version` instance and URL to .alfredworkflow
            file
        :rtype: tuple

        """

        raise NotImplementedError()


class UpdateManager(object):
    """"""

    cache_key_fmt = '__aw_updater-{0}'

    def __init__(self, update_settings, update_interval=ONE_DAY):
        self.update_settings = update_settings
        self.update_interval = update_interval

    def get_updater(self):
        """Return :class:`Updater` instance for :attr:`update_settings`

        """

        results = hooks.get_updater.send(self.update_settings)
        for receiver, updater in results:
            if updater is not None:
                return updater

    def check_for_update(self, force=False):
        """"""
        updater = self.get_updater()
        name = self.cache_key_fmt.format(updater.__class__.__name__)

    def install_update(self):
        """"""
        if self.check_for_update():
            pass
        else:
            log.debug('No update available')
            return False

    @property
    def update_available(self):
        """"""
        updater = self.get_updater()
        name = self.cache_key_fmt.format(updater.__class__.__name__)


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

    wf().logger.debug(
        'Downloading updated workflow from `{0}` to `{1}` ...'.format(
            url, local_path))

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
        raise ValueError('Invalid GitHub slug : {0}'.format(slug))

    return RELEASES_BASE.format(slug)


def get_valid_releases(github_slug):
    """Return list of all valid releases

    :param github_slug: ``username/repo`` for workflow's GitHub repo
    :returns: list of dicts. Each :class:`dict` has the form
        ``{'version': '1.1', 'download_url': 'http://github.com/...'}``


    A valid release is one that contains one ``.alfredworkflow`` file.

    If the GitHub version (i.e. tag) is of the form ``v1.1``, the leading
    ``v`` will be stripped.

    """

    api_url = build_api_url(github_slug)
    releases = []

    wf().logger.debug('Retrieving releases list from `{0}` ...'.format(
                      api_url))

    def retrieve_releases():
        wf().logger.info(
            'Retrieving releases for `{0}` ...'.format(github_slug))
        return web.get(api_url).json()

    slug = github_slug.replace('/', '-')
    for release in wf().cached_data('gh-releases-{0}'.format(slug),
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
            wf().logger.warning(
                'Invalid release {0} : pre-release detected'.format(version))
            continue
        if not download_urls:
            wf().logger.warning(
                'Invalid release {0} : No workflow file'.format(version))
            continue
        if len(download_urls) > 1:
            wf().logger.warning(
                'Invalid release {0} : multiple workflow files'.format(version))
            continue

        wf().logger.debug('Release `{0}` : {1}'.format(version, url))
        releases.append({'version': version, 'download_url': download_urls[0]})

    return releases


def check_update(github_slug, current_version):
    """Check whether a newer release is available on GitHub

    :param github_slug: ``username/repo`` for workflow's GitHub repo
    :param current_version: the currently installed version of the
        workflow. :ref:`Semantic versioning <semver>` is required.
    :type current_version: ``unicode``
    :returns: ``True`` if an update is available, else ``False``

    If an update is available, its version number and download URL will
    be cached.

    """

    releases = get_valid_releases(github_slug)

    wf().logger.info('{0} releases for {1}'.format(len(releases),
                                                   github_slug))

    if not len(releases):
        raise ValueError('No valid releases for {0}'.format(github_slug))

    # GitHub returns releases newest-first
    latest_release = releases[0]

    # (latest_version, download_url) = get_latest_release(releases)
    vr = base.Version(latest_release['version'])
    vl = base.Version(current_version)
    wf().logger.debug('Latest : {0!r} Installed : {1!r}'.format(vr, vl))
    if vr > vl:

        wf().cache_data(base.KEY_UPDATE_DATA, {
            'version': latest_release['version'],
            'download_url': latest_release['download_url'],
            'available': True
        })

        return True

    wf().cache_data(base.KEY_UPDATE_DATA, {
        'available': False
    })
    return False


def install_update(github_slug, current_version):
    """If a newer release is available, download and install it

    :param github_slug: ``username/repo`` for workflow's GitHub repo
    :param current_version: the currently installed version of the
        workflow. :ref:`Semantic versioning <semver>` is required.
    :type current_version: ``unicode``

    If an update is available, it will be downloaded and installed.

    :returns: ``True`` if an update is installed, else ``False``

    """
    # TODO: `github_slug` and `current_version` are both unusued.

    update_data = wf().cached_data(base.KEY_UPDATE_DATA, max_age=0)

    if not update_data or not update_data.get('available'):
        wf().logger.info('No update available')
        return False

    local_file = download_workflow(update_data['download_url'])

    wf().logger.info('Installing updated workflow ...')
    subprocess.call(['open', local_file])

    update_data['available'] = False
    wf().cache_data(base.KEY_UPDATE_DATA, update_data)
    return True


if __name__ == '__main__':  # pragma: nocover
    import sys

    def show_help():
        print('Usage : update.py (check|install) github_slug version')
        sys.exit(1)

    if len(sys.argv) != 4:
        show_help()

    action, github_slug, version = sys.argv[1:]

    if action not in ('check', 'install'):
        show_help()

    if action == 'check':
        check_update(github_slug, version)
    elif action == 'install':
        install_update(github_slug, version)
