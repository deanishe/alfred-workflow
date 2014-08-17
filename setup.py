#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-17
#

import os
from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


version = '1.8.4'
name = 'Alfred-Workflow'
author = 'Dean Jackson'
author_email = 'deanishe@deanishe.net'
url = 'http://www.deanishe.net/alfred-workflow/'
description = 'A Python helper library for writing Alfred 2 workflows.'
packages = ['workflow']
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(name=name,
      version=version,
      description=description,
      long_description=read('README.txt'),
      author=author,
      author_email=author_email,
      url=url,
      packages=packages,
      classifiers=classifiers)
