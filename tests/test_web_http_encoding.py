#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-17
#

"""HTTP unit tests."""


import os

import pytest
import pytest_localserver  # noqa: F401


from workflow import web

TEST_DATA = [
    # Baidu sends charset header *and* uses meta HTML tag
    ('baidu.html', {'Content-Type': 'text/html; charset=utf-8'}, 'utf-8'),

    # Document specifies us-ascii
    ('us-ascii.xml', {'Content-Type': 'application/xml'}, 'us-ascii'),

    # Document specifies UTF-8
    ('utf8.xml', {'Content-Type': 'application/xml'}, 'utf-8'),

    # Document specifies no encoding; application/xml defaults to UTF-8
    # (in this library. There is no standard encoding defined.)
    ('no-encoding.xml', {'Content-Type': 'application/xml'}, 'utf-8'),

    # application/json is UTF-8
    ('utf8.json', {'Content-Type': 'application/json'}, 'utf-8'),
]


def test_web_encoding(httpserver):
    """Test web encoding"""
    test_data = []
    for filename, headers, encoding in TEST_DATA:
        p = os.path.join(os.path.dirname(__file__), 'data', filename)
        test_data.append((p, headers, encoding))
        p2 = '{0}.gz'.format(p)
        if os.path.exists(p2):
            h2 = headers.copy()
            h2['Content-Encoding'] = 'gzip'
            test_data.append((p2, h2, encoding))

    for filepath, headers, encoding in test_data:
        print('filepath={0!r}, headers={1!r}, encoding={2!r}'.format(
              filepath, headers, encoding))

        content = open(filepath, 'rb').read()

        httpserver.serve_content(content, headers=headers)
        r = web.get(httpserver.url)
        r.raise_for_status()
        assert r.encoding == encoding


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
