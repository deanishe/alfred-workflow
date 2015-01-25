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


search_items = [
    ('Test Item One', search.MATCH_STARTSWITH),
    ('test item two', search.MATCH_STARTSWITH),
    ('TwoExtraSpecialTests', search.MATCH_CAPITALS),
    ('this-is-a-test', search.MATCH_ATOM),
    ('the extra special trials', search.MATCH_INITIALS_STARTSWITH),
    ('not the extra special trials', search.MATCH_INITIALS_CONTAIN),
    ('intestinal fortitude', search.MATCH_SUBSTRING),
    ('the splits', search.MATCH_ALLCHARS),
    ('nomatch', 0),
]

search_items_diacritics = [
    # search key, query
    ('Änderungen vorbehalten', 'av'),
    ('Änderungen', 'anderungen'),
    ('überwiegend bewolkt', 'ub'),
    ('überwiegend', 'uberwiegend'),
    ('Öffnungszeiten an Feiertagen', 'offnungszeiten'),
    ('Öffnungszeiten an Feiertagen', 'oaf'),
    ('Fußpilz', 'fuss'),
    ('salé', 'sale')
]


####################################################################
# Tests
####################################################################

def test_punctuation():
    """Punctuation: dumbified"""
    for input, output in punctuation_data:
        assert search.dumbify_punctuation(input) == output


####################################################################
# Filtering
####################################################################

def test_filter_all_rules():
    """Filter: all rules"""
    results = search.filter('test', search_items, key=lambda x: x[0],
                            ascending=True, match_on=search.MATCH_ALL)
    assert len(results) == 8
    # now with scores, rules
    results = search.filter('test', search_items, key=lambda x: x[0],
                            include_score=True, match_on=search.MATCH_ALL)
    assert len(results) == 8
    for item, score, rule in results:
        for value, r in search_items:
            if value == item[0]:
                assert rule == r
    # self.assertTrue(False)


def test_filter_no_caps():
    """Filter: no caps"""
    results = search.filter('test', search_items, key=lambda x: x[0],
                            ascending=True,
                            match_on=search.MATCH_ALL ^ search.MATCH_CAPITALS,
                            include_score=True)
    # self._print_results(results)
    for item, score, rule in results:
        assert rule != search.MATCH_CAPITALS
    # assert len(results) == 7


def test_filter_only_caps():
    """Filter: only caps"""
    results = search.filter('test', search_items, key=lambda x: x[0],
                            ascending=True,
                            match_on=search.MATCH_CAPITALS,
                            include_score=True)
    # self._print_results(results)
    assert len(results) == 1


def test_filter_max_results():
    """Filter: max results"""
    results = search.filter('test', search_items, key=lambda x: x[0],
                            ascending=True, max_results=4)
    assert len(results) == 4


def test_filter_min_score():
    """Filter: min score"""
    results = search.filter('test', search_items, key=lambda x: x[0],
                            ascending=True, min_score=90,
                            include_score=True)
    assert len(results) == 6


def test_filter_folding():
    """Filter: diacritic folding"""
    for key, query in search_items_diacritics:
        results = search.filter(query, [key], min_score=90,
                                include_score=True)
        assert len(results) == 1


def test_filter_no_folding():
    """Filter: folding turned off for non-ASCII query"""
    data = ['fühler', 'fuhler', 'fübar', 'fubar']
    results = search.filter('fü', data)
    assert len(results) == 2


def test_filter_folding_off():
    """Filter: diacritic folding off"""
    for key, query in search_items_diacritics:
        results = search.filter(query, [key], min_score=90,
                                include_score=True,
                                fold_diacritics=False)
        assert len(results) == 0


def test_filter_empty_key():
    """Filter: empty keys are ignored"""
    data = ['bob', 'sue', 'henry']

    def key(s):
        """Return empty key"""
        return ''

    results = search.filter('lager', data, key)
    assert len(results) == 0


def test_filter_empty_query_words():
    """Filter: empty query raises error"""
    data = ['bob', 'sue', 'henry']
    with pytest.raises(ValueError):
        search.filter('   ', data)

    with pytest.raises(ValueError):
        search.filter('', data)


def test_filter_empty_query_words_ignored():
    """Filter: empty query words ignored"""
    data = ['bob jones', 'sue smith', 'henry rogers']
    results = search.filter('bob       jones', data)
    assert len(results) == 1


def test_filter_identical_items():
    """Filter: identical items are not discarded"""
    data = ['bob', 'bob', 'bob']
    results = search.filter('bob', data)
    assert len(results) == len(data)


def test_filter_reversed_results():
    """Filter: results reversed"""
    data = ['bob', 'bobby', 'bobby smith']
    results = search.filter('bob', data)
    assert results == data
    results = search.filter('bob', data, ascending=True)
    assert results == data[::-1]


if __name__ == '__main__':
    pytest.main([__file__])
