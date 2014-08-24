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

.. _updates:

.. versionadded:: 1.9

Add self-updating capabilities to your workflow. It regularly (every day
by default) fetches the latest releases from the specified GitHub repository
and then asks the user if they want to replace the workflow if a newer version
is available.

Currently, only updates from
`GitHub releases <https://help.github.com/categories/85/articles>`_ are
supported.

For your workflow to be able to recognise and download newer versions, the
``version`` value you pass to :class:`~workflow.workflow.Workflow` **must**
be one of the versions (i.e. tags) in the corresponding GitHub repo's
releases list. There must also be one (and only one) ``.alfredworkflow``
binary attached to the newest release. This is the file that will be downloaded
and installed via Alfred's default installation mechanism.

To use this feature, you must pass a :class:`dict` as the ``update_settings``
argument to :class:`~workflow.workflow.Workflow`. It **must** have the two
keys/values ``github_slug``, which is your username and the name of the
workflow's repo in the format ``username/reponame``, and ``version``, which
is the release version (release tag) of the installed workflow, e.g.:

.. code-block:: python
    :linenos:

    from workflow import Workflow

    ...

    wf = Workflow(..., update_settings={
        # Your username and the workflow's repo's name
        'github_slug': 'username/reponame',
        # The version (i.e. release/tag) of the installed workflow
        'version': 'v1.0',
        # Optional number of days between checks for updates
        'frequency': 7
    }, ...)

    ...

    if wf.update_available:
        wf.start_update()

**Alfred-Workflow** will automatically check in the background if a newer
version of your workflow is available, but will not automatically inform the
user. To view update status/install a newer version, the user must either
call one of your workflow's Script Filters with the ``workflow:update``
:ref:`magic argument <magic-arguments>`, in which case **Alfred-Workflow**
will handle the update automatically, or you must add your own update action
using :attr:`Workflow.update_available <workflow.workflow.Workflow.update_available>`
and :meth:`Workflow.start_update() <workflow.workflow.Workflow.start_update>`
to check for and install newer versions.
:meth:`Workflow.start_update() <workflow.workflow.Workflow.start_update>`
returns ``False`` if no update is available, or if one is, it will return
``True``, download the newer version and tell Alfred to install it.

"""

from __future__ import print_function, unicode_literals

import os
import tempfile
import argparse

import workflow
import web

__all__ = []

wf = workflow.Workflow()
log = wf.logger

RELEASES_BASE = 'https://api.github.com/repos/%s/releases'


def _download_workflow(github_url):
    filename = github_url.split("/")[-1]
    if (not github_url.endswith('.alfredworkflow') or
            not filename.endswith('.alfredworkflow')):
        raise ValueError('Attachment %s not a workflow' % filename)
    local_file = os.path.join(tempfile.gettempdir(), filename)
    response = web.get(github_url)
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
    releases = web.get(_get_api_url(github_slug)).json()
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
