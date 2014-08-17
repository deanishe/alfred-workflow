#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8
"""
test_encoding.py

Created by deanishe@deanishe.net on 2014-08-17.
Copyright (c) 2014 deanishe@deanishe.net

MIT Licence. See http://opensource.org/licenses/MIT

"""

from __future__ import print_function


import unittest

from workflow import web


def setUp():
    pass


def tearDown():
    pass


class WebEncodingTests(unittest.TestCase):
    def setUp(self):
        self.urls = [
            # URL, encoding
            ('http://www.baidu.com/s?wd=lager', 'utf-8'),
            ('http://httpbin.org/xml', 'us-ascii'),
            ('http://httpbin.org/get', 'utf-8'),
            ('https://deanishe.net/no-encoding.xml', 'utf-8')
        ]

    def tearDown(self):
        pass

    def test_encoding(self):
        """Find response encoding"""
        for url, encoding in self.urls:
            r = web.get(url)
            self.assertEqual(r.encoding, encoding)


if __name__ == '__main__':
    unittest.main()
