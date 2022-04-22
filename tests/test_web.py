#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-23
#
"""Unit tests for :mod:`workflow.web`"""


import json
import os
import shutil
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode
from pprint import pprint

import pytest
import pytest_localserver  # noqa: F401
from workflow import web

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

HTTPBIN_URL = 'https://eu.httpbin.org'


class CaseInsensitiveDictTests(unittest.TestCase):
    """Unit tests for CaseInsensitiveDict"""

    def setUp(self):
        """Initialise test environment."""
        self.data_list = [('Aardvark', 'a'), ('Booty', 'b'), ('Clown', 'c')]
        self.data_dict = dict(self.data_list)

    def tearDown(self):
        """Reset test environment."""
        pass

    def test_init_dict(self):
        """Initialise CaseInsensitiveDict"""
        d1 = web.CaseInsensitiveDictionary(self.data_list)
        d2 = web.CaseInsensitiveDictionary(self.data_dict)
        self.assertEqual(d1, d2)

    def test_retrieve(self):
        """Retrieve CaseInsensitiveDict values"""
        d = web.CaseInsensitiveDictionary(self.data_list)
        for k, v in self.data_list:
            self.assertEqual(v, d[k])
            self.assertEqual(v, d[k.lower()])
            self.assertEqual(v, d[k.upper()])
            self.assertEqual(v, d[k.title()])
            self.assertEqual(v, d.get(k))
            self.assertEqual(v, d.get(k.lower()))
            self.assertEqual(v, d.get(k.upper()))
            self.assertEqual(v, d.get(k.title()))
            self.assertTrue(k in d)
            self.assertTrue(k.lower() in d)
            self.assertTrue(k.upper() in d)
            self.assertTrue(k.title() in d)

        self.assertTrue(d.get('This is not a key') is None)
        self.assertFalse('This is not a key' in d)

    def test_set(self):
        """Set CaseInsensitiveDict values"""
        d = web.CaseInsensitiveDictionary()
        for k, v in self.data_list:
            self.assertFalse(k in d)

        for k, v in self.data_list:
            d[k.upper()] = v

        for k, v in self.data_list:
            self.assertTrue(k in d)
            self.assertEqual(d[k], v)
            self.assertEqual(d[k.lower()], v)

        d2 = {'Dogs': 'd', 'Elephants': 'e'}
        for k, v in list(d2.items()):
            self.assertFalse(k in d)
            self.assertTrue(d.get(k) is None)

        d.update(d2)

        for k, v in list(d2.items()):
            self.assertTrue(k in d)
            self.assertTrue(k.upper() in d)
            self.assertEqual(d.get(k), v)

    def test_iterators(self):
        """Iterate CaseInsensitiveDict"""
        d = web.CaseInsensitiveDictionary(self.data_dict)

        self.assertEqual(sorted(d.keys()), sorted(self.data_dict.keys()))
        self.assertEqual(sorted(d.values()), sorted(self.data_dict.values()))

        for k in d.keys():
            self.assertTrue(k in self.data_dict)

        values = list(self.data_dict.values())

        for v in d.values():
            self.assertTrue(v in values)

        for t in d.items():
            self.assertTrue(t in self.data_list)


class WebTests(unittest.TestCase):
    """Unit tests for workflow.web"""

    def setUp(self):
        """Initialise unit test environment."""
        self.data = {'name': 'My name is Jürgen!',
                     'address': 'Hürterstr. 42\nEssen'}
        self.test_file = os.path.join(DATA_DIR,
                                      'cönfüsed.gif')
        self.tempdir = os.path.join(tempfile.gettempdir(),
                                    'web_py.{0:d}.tmp'.format(os.getpid()))

    def tearDown(self):
        """Reset unit test environment."""
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_404(self):
        """Non-existant URL raises HTTPError w/ 404"""
        url = HTTPBIN_URL + '/status/404'
        r = web.get(url)
        self.assertRaises(urllib.error.HTTPError, r.raise_for_status)
        self.assertTrue(r.status_code == 404)

    def test_follow_redirect(self):
        """Redirects are followed"""
        url = HTTPBIN_URL + '/redirect-to?url=' + HTTPBIN_URL
        r = web.get(url)
        self.assertEqual(r.url.rstrip('/'), HTTPBIN_URL.rstrip('/'))

    def test_no_follow_redirect(self):
        """Redirects are not followed"""
        url = HTTPBIN_URL + '/redirect-to?url=' + HTTPBIN_URL
        r = web.get(url, allow_redirects=False)
        self.assertNotEqual(r.url, HTTPBIN_URL)
        self.assertRaises(urllib.error.HTTPError, r.raise_for_status)
        self.assertEqual(r.status_code, 302)

    def test_post_form(self):
        """POST Form data"""
        url = HTTPBIN_URL + '/post'
        r = web.post(url, data=self.data)
        self.assertTrue(r.status_code == 200)
        r.raise_for_status()
        form = r.json()['form']
        for key in self.data:
            self.assertTrue(form[key] == self.data[key])

    def test_post_json(self):
        """POST request with JSON body"""
        url = HTTPBIN_URL + '/post'
        headers = {'content-type': 'application/json'}
        r = web.post(url, headers=headers, data=json.dumps(self.data))
        self.assertTrue(r.status_code == 200)
        data = r.json()
        pprint(data)
        self.assertEqual(data['headers']['Content-Type'], 'application/json')
        for key in self.data:
            self.assertTrue(data['json'][key] == self.data[key])

    def test_post_without_data(self):
        """POST request without data"""
        url = HTTPBIN_URL + '/post'
        r = web.post(url)
        self.assertTrue(r.status_code == 200)
        r.raise_for_status()

    def test_put_form(self):
        """PUT Form data"""
        url = HTTPBIN_URL + '/put'
        r = web.put(url, data=self.data)
        self.assertTrue(r.status_code == 200)
        r.raise_for_status()
        form = r.json()['form']
        for key in self.data:
            self.assertTrue(form[key] == self.data[key])

    def test_put_json(self):
        """PUT request with JSON body"""
        url = HTTPBIN_URL + '/delete'
        headers = {'content-type': 'application/json'}
        r = web.delete(url, headers=headers, data=json.dumps(self.data))
        self.assertTrue(r.status_code == 200)
        data = r.json()
        pprint(data)
        self.assertEqual(data['headers']['Content-Type'], 'application/json')
        for key in self.data:
            self.assertTrue(data['json'][key] == self.data[key])

    def test_put_without_data(self):
        """PUT request without data"""
        url = HTTPBIN_URL + '/put'
        r = web.put(url)
        self.assertTrue(r.status_code == 200)
        r.raise_for_status()

    def test_delete(self):
        """DELETE request"""
        url = HTTPBIN_URL + '/delete'
        r = web.delete(url)
        pprint(r.json())
        self.assertTrue(r.status_code == 200)
        r.raise_for_status()

    def test_delete_with_json(self):
        """DELETE request with JSON body"""
        url = HTTPBIN_URL + '/delete'
        headers = {'content-type': 'application/json'}
        r = web.delete(url, headers=headers, data=json.dumps(self.data))
        self.assertTrue(r.status_code == 200)
        data = r.json()
        pprint(data)
        self.assertEqual(data['headers']['Content-Type'], 'application/json')
        for key in self.data:
            self.assertTrue(data['json'][key] == self.data[key])

    def test_timeout(self):
        """Request times out"""
        url = HTTPBIN_URL + '/delay/3'
        if sys.version_info < (2, 7):
            self.assertRaises(urllib.error.URLError, web.get, url, timeout=1)
        else:
            self.assertRaises(socket.timeout, web.get, url, timeout=1)

    def test_encoding(self):
        """HTML is decoded"""
        url = HTTPBIN_URL + '/html'
        r = web.get(url)
        self.assertEqual(r.encoding, 'utf-8')
        self.assertTrue(isinstance(r.text, str))

    def test_no_encoding(self):
        """No encoding"""
        # Is an image
        url = HTTPBIN_URL + '/bytes/100'
        r = web.get(url)
        self.assertEqual(r.encoding, None)
        self.assertTrue(isinstance(r.text, bytes))

    def test_html_encoding(self):
        """HTML is decoded"""
        url = HTTPBIN_URL + '/html'
        r = web.get(url)
        self.assertEqual(r.encoding, 'utf-8')
        self.assertTrue(isinstance(r.text, str))

    def test_default_encoding(self):
        """Default encodings for mimetypes."""
        url = HTTPBIN_URL + '/response-headers'
        r = web.get(url)
        r.raise_for_status()
        # httpbin returns JSON by default. web.py should automatically
        # set `encoding` to UTF-8 when mimetype = 'application/json'
        assert r.encoding == 'utf-8'
        assert isinstance(r.text, str)

    def test_xml_encoding(self):
        """XML is decoded."""
        url = HTTPBIN_URL + '/response-headers'
        params = {'Content-Type': 'text/xml; charset=UTF-8'}
        r = web.get(url, params)
        r.raise_for_status()
        assert r.encoding == 'utf-8'
        assert isinstance(r.text, str)

    def test_get_vars(self):
        """GET vars"""
        url = HTTPBIN_URL + '/get'
        r = web.get(url, params=self.data)
        self.assertEqual(r.status_code, 200)
        args = r.json()['args']
        for key in self.data:
            self.assertEqual(args[key], self.data[key])

    def test_auth_succeeds(self):
        """Basic AUTH succeeds"""
        url = HTTPBIN_URL + '/basic-auth/bobsmith/password1'
        r = web.get(url, auth=('bobsmith', 'password1'))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['user'], 'bobsmith')
        self.assertTrue(data['authenticated'])

    def test_auth_fails(self):
        """Basic AUTH fails"""
        url = HTTPBIN_URL + '/basic-auth/bobsmith/password1'
        r = web.get(url, auth=('bobsmith', 'password2'))
        self.assertEqual(r.status_code, 401)
        self.assertRaises(urllib.error.HTTPError, r.raise_for_status)

    def test_file_upload(self):
        """File upload"""
        url = HTTPBIN_URL + '/post'
        files = {'file': {'filename': 'cönfüsed.gif',
                          'content': open(self.test_file, 'rb').read(),
                          'mimetype': 'image/gif',
                          }}
        r = web.post(url, data=self.data, files=files)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        form = data['form']
        for key in self.data:
            self.assertEqual(self.data[key], form[key])
        # image
        bindata = data['files']['file']
        preamble = 'data:image/gif;base64,'
        self.assertTrue(bindata.startswith(preamble))
        bindata = b64decode(bindata[len(preamble):])
        self.assertEqual(bindata, open(self.test_file, 'rb').read())

    def test_file_upload_without_form_data(self):
        """File upload w/o form data"""
        url = HTTPBIN_URL + '/post'
        files = {'file': {'filename': 'cönfüsed.gif',
                          'content': open(self.test_file, 'rb').read()
                          }}
        r = web.post(url, files=files)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # image
        bindata = data['files']['file']
        preamble = 'data:image/gif;base64,'
        self.assertTrue(bindata.startswith(preamble))
        bindata = b64decode(bindata[len(preamble):])
        self.assertEqual(bindata, open(self.test_file, 'rb').read())

    def test_file_upload_with_unicode(self):
        """File upload with Unicode contents is converted to bytes"""
        url = HTTPBIN_URL + '/post'
        content = 'Hére ïs søme ÜÑÎÇÒDÈ™'
        files = {'file': {'filename': 'cönfüsed.txt',
                          'content': content
                          }}
        r = web.post(url, files=files)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        bindata = data['files']['file']
        self.assertEqual(bindata, content)

    def test_json_encoding(self):
        """JSON decoded correctly"""
        url = HTTPBIN_URL + '/get'
        params = {'town': 'münchen'}
        r = web.get(url, params)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['args']['town'], 'münchen')

    def test_gzipped_content(self):
        """Gzipped content decoded"""
        url = HTTPBIN_URL + '/gzip'
        r = web.get(url)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data.get('gzipped'))

    def test_gzipped_iter_content(self):
        """Gzipped iter_content decoded"""
        url = HTTPBIN_URL + '/gzip'
        r = web.get(url, stream=True)
        self.assertEqual(r.status_code, 200)
        data = b''
        for b in r.iter_content():
            data += b
        data = json.loads(data)
        self.assertTrue(data.get('gzipped'))

    def test_params_added_to_url(self):
        """`params` are added to existing GET args"""
        url = HTTPBIN_URL + '/get?existing=one'
        r = web.get(url)
        r.raise_for_status()
        args = r.json()['args']
        print('args=%r' % args)
        self.assertEqual(args.get('existing'), 'one')

        # Add additional params
        params = {'extra': 'two'}
        r = web.get(url, params)
        r.raise_for_status()
        args = r.json()['args']
        print('args=%r' % args)
        self.assertEqual(args.get('existing'), 'one')
        self.assertEqual(args.get('extra'), 'two')


#                     dP                       dP
#                     88                       88
# 88d888b. dP    dP d8888P .d8888b. .d8888b. d8888P
# 88'  `88 88    88   88   88ooood8 Y8ooooo.   88
# 88.  .88 88.  .88   88   88.  ...       88   88
# 88Y888P' `8888P88   dP   `88888P' `88888P'   dP
# 88            .88
# dP        d8888P

fubar_path = os.path.join(DATA_DIR, 'fubar.txt')
fubar_bytes = open(fubar_path, 'rb').read()
fubar_unicode = str(fubar_bytes, 'utf-8')

utf8html_path = os.path.join(DATA_DIR, 'utf8.html')
utf8html_bytes = open(utf8html_path, 'rb').read()
utf8html_unicode = str(utf8html_bytes, 'utf-8')

utf8xml_path = os.path.join(DATA_DIR, 'utf8.xml')
utf8xml_bytes = open(utf8xml_path, 'rb').read()
utf8xml_unicode = str(utf8xml_bytes, 'utf-8')

gifpath = os.path.join(DATA_DIR, 'cönfüsed.gif')
gifbytes = open(gifpath, 'rb').read()

gifpath_gzip = os.path.join(DATA_DIR, 'cönfüsed.gif.gz')
gifbytes_gzip = open(gifpath_gzip, 'rb').read()

tempdir = os.path.join(tempfile.gettempdir(),
                       'web_py.{0}.tmp'.format(os.getpid()))


def test_charset_sniffing(httpserver):
    """Charset sniffing for HTML and XML"""
    for data, typ in ((utf8html_bytes, 'text/html'),
                      (utf8xml_bytes, 'text/xml'),
                      (utf8xml_bytes, 'application/xml')):
        httpserver.serve_content(data, headers={'Content-Type': typ})
        r = web.get(httpserver.url)
        r.raise_for_status()
        assert r.encoding == 'utf-8'
        assert isinstance(r.text, str)


def test_save_to_path(httpserver):
    """Save directly to file"""
    filepath = os.path.join(tempdir, 'fubar.txt')
    assert not os.path.exists(tempdir)
    assert not os.path.exists(filepath)
    httpserver.serve_content(fubar_bytes,
                             headers={'Content-Type': 'text/plain'})
    try:
        r = web.get(httpserver.url)
        assert r.status_code == 200
        r.save_to_path(filepath)

        assert os.path.exists(filepath)
        data = open(filepath, 'rb').read()
        assert data == fubar_bytes

    finally:
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)


def test_save_to_path_fails(httpserver):
    """Save to file fails if `content` has been accessed"""
    filepath = os.path.join(tempdir, 'fubar.txt')
    httpserver.serve_content(fubar_bytes,
                             headers={'Content-Type': 'text/plain'})
    r = web.get(httpserver.url)
    r.content
    with pytest.raises(RuntimeError):
        r.save_to_path(filepath)

    if os.path.exists(filepath):
        os.unlink(filepath)


def test_iter_content(httpserver):
    """iter_content bytes"""
    httpserver.serve_content(fubar_bytes,
                             headers={'Content-Type': 'text/plain'})
    r = web.get(httpserver.url, stream=True)
    assert r.status_code == 200
    contents = b''
    for s in r.iter_content(chunk_size=1):
        contents += s
    assert contents == fubar_bytes


def test_iter_content_decoded(httpserver):
    """iter_content decoded"""
    httpserver.serve_content(fubar_bytes, headers={
                             'Content-Type':
                             'text/plain; charset=UTF-8'})
    r = web.get(httpserver.url, stream=True)
    assert r.status_code == 200
    contents = ''
    for s in r.iter_content(chunk_size=1, decode_unicode=True):
        contents += s
    assert contents == fubar_unicode


def test_iter_content_nosniff(httpserver):
    """iter_content doesn't sniff content"""
    # Content isn't sniffed when streaming
    httpserver.serve_content(utf8html_bytes)
    r = web.get(httpserver.url, stream=True)
    it = r.iter_content(decode_unicode=True)
    for chunk in it:
        pass
    print('r.encoding=%r' % r.encoding)
    assert r.encoding is None

    # Pass content-type but no encoding
    httpserver.serve_content(utf8html_bytes,
                             headers={'Content-Type': 'text/html'})
    r = web.get(httpserver.url, stream=True)
    it = r.iter_content(decode_unicode=True)
    for chunk in it:
        pass
    assert r.encoding is None

    # Encoding read from HTTP header
    httpserver.serve_content(
        utf8html_bytes,
        headers={'Content-Type': 'text/html; charset=ascii'})
    r = web.get(httpserver.url, stream=True)
    for k in r.headers:
        print('%r=%r' % (k, r.headers[k]))
    it = r.iter_content(decode_unicode=True)
    for chunk in it:
        pass
    assert r.encoding == 'ascii'

    # Encoding properly sniffed
    httpserver.serve_content(
        utf8html_bytes,
        headers={'Content-Type': 'text/html'})
    r = web.get(httpserver.url)
    assert r.encoding == 'utf-8'


def test_iter_content_requires_stream(httpserver):
    """iter_content fails if `stream` is `False`"""
    httpserver.serve_content(utf8html_bytes)
    r = web.get(httpserver.url)
    with pytest.raises(RuntimeError):
        r.iter_content(decode_unicode=True)


def test_iter_content_fails_if_content_read(httpserver):
    """iter_content fails if `content` has been read"""
    httpserver.serve_content(utf8html_bytes)
    r = web.get(httpserver.url, stream=True)
    r.content
    with pytest.raises(RuntimeError):
        r.iter_content(decode_unicode=True)


def test_encoded_content(httpserver):
    """Content decoding"""
    httpserver.serve_content(fubar_bytes, headers={
                             'Content-Type':
                             'text/plain; charset=UTF-8'})
    r = web.get(httpserver.url)
    assert r.status_code == 200
    assert r.content == fubar_bytes
    assert r.text == fubar_unicode


def test_xml_content(httpserver):
    """Correct mimetype for application/xml"""
    httpserver.serve_content(utf8xml_bytes, headers={
                             'Content-Type': 'application/xml'})
    r = web.get(httpserver.url, stream=True)
    assert r.encoding == 'utf-8'


def test_gzipped_content(httpserver):
    """Gzip encoding"""
    httpserver.serve_content(gifbytes,
                             headers={'Content-Type': 'image/gif'})
    r = web.get(httpserver.url)
    assert r.status_code == 200
    assert r.content == gifbytes

    httpserver.serve_content(
        gifbytes_gzip,
        headers={
            'Content-Type': 'image/gif',
            'Content-Encoding': 'gzip',
        })
    # Full response
    r = web.get(httpserver.url)
    assert r.status_code == 200
    assert r.content == gifbytes
    # Streamed response
    r = web.get(httpserver.url, stream=True)
    assert r.status_code == 200
    content = b''
    for chunk in r.iter_content():
        content += chunk
    assert content == gifbytes


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
