#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-23
#
"""
test_web2.py

"""

from __future__ import print_function, unicode_literals


import os

import pytest
import pytest_httpbin

from workflow import web


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


# Broken. Why doesn't this work with the local httpbin?
def no_test_default_encoding(httpbin):
    """Default encodings for mimetypes."""
    url = httpbin.url + '/response-headers'
    r = web.get(url)
    r.raise_for_status()
    # httpbin returns JSON by default. web.py should automatically
    # set `encoding` to UTF-8 when mimetype = 'application/json'
    assert r.encoding == 'utf-8'
    assert isinstance(r.text, unicode)


# Broken. Why doesn't this work with the local httpbin?
def no_test_xml_encoding(httpbin):
    """XML is decoded."""
    url = httpbin.url + '/response-headers'
    params = {'Content-Type': 'text/xml; charset=UTF-8'}
    r = web.get(url, params)
    r.raise_for_status()
    assert r.encoding == 'utf-8'
    assert isinstance(r.text, unicode)


def test_default_encoding_remote(httpbin):
    """Default encodings for mimetypes."""
    url = 'http://httpbin.org/response-headers'
    r = web.get(url)
    r.raise_for_status()
    # httpbin returns JSON by default. web.py should automatically
    # set `encoding` to UTF-8 when mimetype = 'application/json'
    assert r.encoding == 'utf-8'
    assert isinstance(r.text, unicode)


def test_xml_encoding_remote(httpbin):
    """XML is decoded."""
    url = 'http://httpbin.org/response-headers'
    params = {'Content-Type': 'text/xml; charset=UTF-8'}
    r = web.get(url, params)
    r.raise_for_status()
    assert r.encoding == 'utf-8'
    assert isinstance(r.text, unicode)

if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
