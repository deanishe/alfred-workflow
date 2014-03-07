#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-01
#
"""
test_web.py

"""

from __future__ import print_function, unicode_literals


import os
import unittest
import urllib2
import json
import socket
from base64 import b64decode
from pprint import pprint
from workflow import web


BASE_URL = 'http://eu.httpbin.org/'


def setUp():
    pass


def tearDown():
    pass


class WebTests(unittest.TestCase):

    def setUp(self):
        self.data = {'name': 'My name is Jürgen!',
                     'address': 'Hürterstr. 42\nEssen'}
        self.test_file = os.path.join(os.path.dirname(__file__),
                                      'cönfüsed.gif')

    def tearDown(self):
        pass

    def test_404(self):
        """Non-existant URL raises HTTPError w/ 404"""
        url = BASE_URL + 'status/404'
        r = web.get(url)
        self.assertRaises(urllib2.HTTPError, r.raise_for_status)
        self.assert_(r.status_code == 404)

    def test_follow_redirect(self):
        """Redirects are followed"""
        newurl = 'http://www.kulturliste-duesseldorf.de/'
        url = BASE_URL + 'redirect-to?url=' + newurl
        r = web.get(url)
        self.assertEquals(r.url, newurl)

    def test_no_follow_redirect(self):
        """Redirects are not followed"""
        newurl = 'http://www.kulturliste-duesseldorf.de/'
        url = BASE_URL + 'redirect-to?url=' + newurl
        r = web.get(url, allow_redirects=False)
        self.assertNotEquals(r.url, newurl)
        self.assertRaises(urllib2.HTTPError, r.raise_for_status)
        self.assertEquals(r.status_code, 302)

    def test_post_form(self):
        """POST Form data"""
        url = BASE_URL + 'post'
        r = web.post(url, data=self.data)
        self.assert_(r.status_code == 200)
        r.raise_for_status()
        form = r.json()['form']
        for key in self.data:
            self.assert_(form[key] == self.data[key])

    def test_post_json(self):
        """POST request with JSON body"""
        url = BASE_URL + 'post'
        headers = {'content-type': 'application/json'}
        print('Posting JSON ...')
        r = web.post(url, headers=headers, data=json.dumps(self.data))
        self.assert_(r.status_code == 200)
        data = r.json()
        pprint(data)
        self.assertEquals(data['headers']['Content-Type'],
                          'application/json')
        for key in self.data:
            self.assert_(data['json'][key] == self.data[key])
        return

    def test_timeout(self):
        """Request times out"""
        url = BASE_URL + 'delay/10'
        self.assertRaises(socket.timeout, web.get, url, timeout=5)

    def test_encoding(self):
        """HTML is decoded"""
        url = BASE_URL + 'html'
        r = web.get(url)
        self.assertEquals(r.encoding, 'utf-8')
        self.assert_(isinstance(r.text, unicode))

    def test_no_encoding(self):
        """No encoding"""
        # Is an image
        url = 'https://avatars.githubusercontent.com/u/747913'
        r = web.get(url)
        self.assertEquals(r.encoding, None)
        self.assert_(isinstance(r.text, str))

    def test_xml_encoding(self):
        """XML is decoded"""
        url = 'http://feeds.theguardian.com/theguardian/technology/rss'
        r = web.get(url)
        self.assertEquals(r.encoding, 'utf-8')
        self.assert_(isinstance(r.text, unicode))

    def test_get_vars(self):
        """GET vars"""
        url = BASE_URL + 'get'
        r = web.get(url, params=self.data)
        self.assertEquals(r.status_code, 200)
        args = r.json()['args']
        for key in self.data:
            self.assertEquals(args[key], self.data[key])

    def test_auth_succeeds(self):
        """Basic AUTH succeeds"""
        url = BASE_URL + '/basic-auth/bobsmith/password1'
        r = web.get(url, auth=('bobsmith', 'password1'))
        self.assertEquals(r.status_code, 200)
        data = r.json()
        self.assertEquals(data['user'], 'bobsmith')
        self.assertTrue(data['authenticated'])

    def test_auth_fails(self):
        """Basic AUTH fails"""
        url = BASE_URL + '/basic-auth/bobsmith/password1'
        r = web.get(url, auth=('bobsmith', 'password2'))
        self.assertEquals(r.status_code, 401)
        self.assertRaises(urllib2.HTTPError, r.raise_for_status)

    def test_file_upload(self):
        """File upload"""
        url = BASE_URL + 'post'
        files = {'file': {'filename': 'cönfüsed.gif',
                          'content': open(self.test_file, 'rb').read(),
                          'mimetype': 'image/gif',
                          }}
        r = web.post(url, data=self.data, files=files)
        self.assertEquals(r.status_code, 200)
        data = r.json()
        form = data['form']
        for key in self.data:
            self.assertEquals(self.data[key], form[key])
        # image
        bindata = data['files']['file']
        preamble = 'data:image/gif;base64,'
        self.assert_(bindata.startswith(preamble))
        bindata = b64decode(bindata[len(preamble):])
        self.assertEquals(bindata, open(self.test_file, 'rb').read())

    def test_file_upload_without_form_data(self):
        """File upload w/o form data"""
        url = BASE_URL + 'post'
        files = {'file': {'filename': 'cönfüsed.gif',
                          'content': open(self.test_file, 'rb').read()
                          }}
        r = web.post(url, files=files)
        self.assertEquals(r.status_code, 200)
        data = r.json()
        # image
        bindata = data['files']['file']
        preamble = 'data:image/gif;base64,'
        self.assert_(bindata.startswith(preamble))
        bindata = b64decode(bindata[len(preamble):])
        self.assertEquals(bindata, open(self.test_file, 'rb').read())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
