#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-10-02
#

"""Generate a list of workflows on Packal that use Alfred-Workflow."""



import argparse
import csv
import json
import logging
import os
import re
import subprocess
from time import time
from xml.etree import ElementTree as ET
from zipfile import ZipFile

match_zip = re.compile(r'alfred-workflow-.*\.zip').search
is_github_url = re.compile(r'^https?://github.com/.+$').match
parse_github_url = re.compile(r'https?://github.com/(.+?)/(.+)').match

WORKFLOW_LIST = os.path.join(os.path.dirname(__file__),
                             'library_workflows.tsv')
PACKAL_REPO_URL = 'https://github.com/packal/repository'
PACKAL_REPO_DIR = os.path.expanduser('~/Temp/Packal-Repository')
CACHE_PATH = os.path.expanduser('~/.packal_repo_cache.json')
COOKIE_PATH = os.path.expanduser('~/.packal_repo_cookies.txt')

USER_AGENT = 'Alfred-Workflow/1.27 (www.deanishe.net/alfred-workflow/)'

MAX_CACHE_AGE = 7  # days

logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S')

log = logging.getLogger()
log.setLevel(logging.INFO)


def fetch_url(url):
    """Return contents of ``url``."""
    cmd = [
        'curl',
        '--referer', 'http://www.packal.org/workflow-list;auto',
        '--location',
        '--user-agent', USER_AGENT,
        '--silent', '--show-error',
        '--cookie-jar', COOKIE_PATH,
        '--cookie', COOKIE_PATH,
        url]
    data = subprocess.check_output(cmd).decode('utf-8')
    return data


class Cache(object):
    """Cache workflow data scraped from Packal."""

    find_github_url = re.compile(r"""field-github-url
                                 .*?
                                 href="(.+?)"
                                 .*?
                                 </div>""",
                                 re.DOTALL | re.VERBOSE).search

    def __init__(self, filepath):
        """Create new `Cache` at `filepath`."""
        self.filepath = filepath
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath) as file_obj:
                self._data = json.load(file_obj)

    def save(self):
        """Save cache as JSON to `self.filepath`."""
        with open(self.filepath, 'w') as file_obj:
            json.dump(self._data, file_obj, indent=2, sort_keys=True)

    def add_github_info(self, workflow):
        """Add GitHub info to workflow dict.

        {
            'github_user': 'github username',
            'github_repo': 'github repo',
            'github_repo_url': 'https://github.com/user/repo',
            'github_user_url': 'https://github.com/user',
        }
        """
        update = True
        data = {}

        if workflow['bundle'] in self._data:
            data = self._data[workflow['bundle']]
            cache_age = time() - data['cached']
            log.debug('Cache age of %s : %0.3f days', workflow['bundle'],
                      cache_age / 86400)
            if cache_age < (MAX_CACHE_AGE * 86400):
                update = False

            if not update:
                workflow.update(data)
                return workflow

        if update:  # Fetch workflow pages from Packal and grab GitHub info
            log.info('Retrieving %s ...', workflow['url'])
            html = fetch_url(workflow['url'])
            # log.debug(html)
            m = self.find_github_url(html)
            if not m:
                log.warning('No Github info for `%s`', workflow['bundle'])
            else:
                github_url = m.group(1)
                m = parse_github_url(github_url)
                if m:
                    username, repo = m.groups()
                    data['github_user'] = username
                    data['github_repo'] = repo
                    data['github_repo_url'] = github_url
                    data['github_user_url'] = 'https://github.com/{}/'.format(
                        username)

            data['cached'] = time()
            self._data[workflow['bundle']] = data
            self.save()

        workflow.update(data)

        return workflow


def workflow_link(workflow, rest=False, github_links=True):
    """Return a link for ``workflow`` in Markdown or ReST."""
    output = []

    if rest:
        output.append('`{name} <{url}>`__')

        if (github_links and workflow.get('github_repo_url') and
                workflow['github_repo_url'] != workflow['url']):
            output.append('(`GitHub repo <{github_repo_url}>`__)')

        if workflow.get('author_url'):
            if (github_links and workflow.get('github_user_url') and
                    workflow['github_user_url'] != workflow['author_url']):
                output.append('by `{author} <{author_url}>`__')
                output.append('(`on GitHub <{github_user_url}>`__).')
            else:
                output.append('by `{author} <{author_url}>`__.')
        else:
            output.append('by {author}.')

        output.append('{description}')

        return '\n  '.join(output).format(**workflow)

    else:  # Markdown
        output.append('[{name}]({url})')

        if (github_links and workflow.get('github_repo_url') and
                workflow['github_repo_url'] != workflow['url']):
            output.append('([GitHub repo]({github_repo_url}))')

        if workflow.get('author_url'):
            if (github_links and workflow.get('github_user_url') and
                    workflow['github_user_url'] != workflow['author_url']):
                output.append('by [{author}]({author_url})')
                output.append('([on GitHub]({github_user_url})).')
            else:
                output.append('by [{author}]({author_url}).')
        else:
            output.append(' by {author}.')

        output.append('\n  {description}')

        if rest:
            return '\n  '.join(output).format(**workflow)
        else:
            return ' '.join(output).format(**workflow)


def update_repo():
    """Ensure Packal repo is present and up-to-date."""
    if not os.path.exists(PACKAL_REPO_DIR):  # Clone repo
        cmd = ['git', 'clone', PACKAL_REPO_URL, PACKAL_REPO_DIR]
        subprocess.call(cmd)

    else:  # Update repo
        cwd = os.getcwd()
        os.chdir(PACKAL_REPO_DIR)
        cmd = ['git', 'pull']
        subprocess.call(cmd)
        os.chdir(cwd)


def read_list(path):
    """Read list of workflows from a TSV file."""
    workflows = []
    with open(path) as file_obj:
        reader = csv.DictReader(file_obj, delimiter=b'\t')
        for workflow in reader:
            # Decode text
            # log.debug('workflow=%r', workflow)
            for k, v in list(workflow.items()):
                if v is not None:
                    workflow[k] = v.decode('utf-8')

            if is_github_url(workflow.get('url') or ''):
                m = parse_github_url(workflow['url'])
                if m:
                    username, repo = m.groups()
                    workflow['github_user'] = username
                    workflow['github_repo'] = repo
                    workflow['github_repo_url'] = workflow['url']
                    workflow['github_user_url'] = ('https://github.com/{}/'
                                                   .format(username))
                    if not workflow.get('author_url'):
                        workflow['author_url'] = workflow['github_user_url']
            workflows.append(workflow)

    return workflows


def read_manifest(path):
    """Read dictionary of workflows from the Packal manifest.xml file."""
    workflows = {}
    tree = ET.parse(path)
    root = tree.getroot()
    for workflow in root:
        data = {'packal': True}
        for child in workflow:
            if child.tag == 'short':
                data['description'] = child.text.strip()
            else:
                data[child.tag] = child.text.strip() if child.text else None
            # print(child.tag, ':', child.text)
        data['author_url'] = packal_user_url(data['author'])
        if 'bundle' in data:
            workflows[data['bundle']] = data
    return workflows


def workflows_using_aw(dirpath):
    """Yield bundle IDs of workflows using AW."""
    for root, _, filenames in os.walk(dirpath):
        for filename in filenames:
            if not filename.endswith('.alfredworkflow'):
                continue
            path = os.path.join(root, filename)
            with ZipFile(path) as z:
                uses_alfred_workflow = False
                for name in z.namelist():
                    if name in (b'workflow/workflow.py', b'workflow.zip'):
                        uses_alfred_workflow = True
                    elif match_zip(name):
                        uses_alfred_workflow = True
                if uses_alfred_workflow:
                    bundle = os.path.basename(os.path.dirname(path))
                    # print(bundle)
                    yield bundle


def packal_username(author):
    """Format usernames for Packal."""
    user = author.lower()
    user = user.replace(' ', '-')
    return user


def packal_user_url(author):
    """Generate link to Packal page for `author`."""
    return 'http://www.packal.org/users/{}'.format(packal_username(author))


def main():
    """Run script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--bundleid', action='store_true', default=False,
                        help="Print a list of bundle IDs.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Generate debug messages.")
    parser.add_argument('-r', '--rest', action='store_true', default=False,
                        help='Generate ReST list (default is Markdown)')
    parser.add_argument('-g', '--github', action='store_true',
                        default=False,
                        help='Add GitHub links to repo/user profile.'
                        ' Default is no extra links.')
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    log.debug('args=%r', args)

    cache = Cache(CACHE_PATH)
    update_repo()

    workflows = read_list(WORKFLOW_LIST)

    packal_workflows = read_manifest(os.path.join(PACKAL_REPO_DIR,
                                                  'manifest.xml'))

    bundles = []

    log.info('Searching %s...', PACKAL_REPO_DIR)

    for bundle in workflows_using_aw(PACKAL_REPO_DIR):
        if bundle in packal_workflows:
            bundles.append(bundle)
    # print('\n\n')
    log.info('%d Packal workflows using Alfred-Workflow', len(bundles))

    output = []
    for bundle in bundles:
        workflow = packal_workflows[bundle]
        workflow['username'] = packal_username(workflow['author'])
        workflow = cache.add_github_info(workflow)
        workflows.append(workflow)

    log.info('%d workflows using Alfred-Workflow', len(workflows))

    for workflow in workflows:
        if args.bundleid:
            # print(workflow.keys())
            # return
            output.append((workflow['name'], workflow['bundle']))
        else:
            msg = workflow_link(workflow, rest=args.rest,
                                github_links=args.github)
            if not msg.endswith('.'):
                msg += '.'
            output.append((workflow['name'], msg))

    output.sort(key=lambda s: s[0].lower())
    output = [t[1] for t in output]

    for line in output:
        print(('- {}'.format(line).encode('utf-8')))


if __name__ == '__main__':
    main()
