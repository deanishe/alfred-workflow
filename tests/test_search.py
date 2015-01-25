#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-25
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import pytest

from workflow import search


punctuation_data = [
    ('"test"', '"test"'),
    ('„wat denn?“', '"wat denn?"'),
    ('‚wie dat denn?‘', "'wie dat denn?'"),
    ('“test”', '"test"'),
    ('and—why—not', 'and-why-not'),
    ('10–20', '10-20'),
    ('Shady’s back', "Shady's back"),
]


def test_punctuation(self):
    """Punctuation: dumbified"""
    for input, output in punctuation_data:
        assert search.dumbify_punctuation(input) == output


if __name__ == '__main__':
    pytest.main([__file__])
