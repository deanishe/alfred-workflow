#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-17
#

"""Alfred-Workflow library for building Alfred 3/4 workflows."""

import os
from os.path import dirname, join
import subprocess
from setuptools import setup
from setuptools.command.test import test as TestCommand


def read(fname):
    """Return contents of file `fname` in this directory."""
    return open(join(dirname(__file__), fname)).read()


class PyTestCommand(TestCommand):
    """Enable running tests with `python setup.py test`."""

    def finalize_options(self):
        """Implement TestCommand."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Implement TestCommand."""
        subprocess.call(
            ['/bin/bash', join(dirname(__file__), 'run-tests.sh')])


version = read('workflow/version')
long_description = read('README_PYPI.rst')

name = 'Alfred-Workflow'
author = 'Dean Jackson'
author_email = 'deanishe@deanishe.net'
url = 'http://www.deanishe.net/alfred-workflow/'
description = 'Full-featured helper library for writing Alfred 2/3/4 workflows'
keywords = 'alfred workflow alfred4'
packages = ['workflow']
package_data = {'workflow': ['version', 'Notify.tgz']}
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]
install_requires = [
    'six',
    'requests>=2.25,<3',
]
tests_require = [
    'coverage',
    'pyobjc-framework-Cocoa==5.3',
    'pytest==4.6.10',
    'pytest-cov==2.8.1',
    'pytest-httpbin==1.0.0',
    'pytest-localserver==0.5.0',
    'flake8==3.8.1',
    'flake8-docstrings==1.5.0',
]

zip_safe = False

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    keywords=keywords,
    author=author,
    author_email=author_email,
    url=url,
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    classifiers=classifiers,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTestCommand},
    zip_safe=zip_safe,
)
