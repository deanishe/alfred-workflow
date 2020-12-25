# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created 2019-05-05

"""Unit tests for :meth:`workflow.Workflow.filter`."""



import pytest

from workflow.workflow import (
    MATCH_ALL, MATCH_ALLCHARS,
    MATCH_ATOM, MATCH_CAPITALS, MATCH_STARTSWITH,
    MATCH_SUBSTRING, MATCH_INITIALS_CONTAIN,
    MATCH_INITIALS_STARTSWITH,
)

SEARCH_ITEMS = [
    ('Test Item One', MATCH_STARTSWITH),
    ('test item two', MATCH_STARTSWITH),
    ('TwoExtraSpecialTests', MATCH_CAPITALS),
    ('this-is-a-test', MATCH_ATOM),
    ('the extra special trials', MATCH_INITIALS_STARTSWITH),
    ('not the extra special trials', MATCH_INITIALS_CONTAIN),
    ('intestinal fortitude', MATCH_SUBSTRING),
    ('the splits', MATCH_ALLCHARS),
    ('nomatch', 0),
]

SEARCH_ITEMS_DIACRITICS = [
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

PUNCTUATION_DATA = [
    ('"test"', '"test"'),
    ('„wat denn?“', '"wat denn?"'),
    ('‚wie dat denn?‘', "'wie dat denn?'"),
    ('“test”', '"test"'),
    ('and—why—not', 'and-why-not'),
    ('10–20', '10-20'),
    ('Shady’s back', "Shady's back"),
]


def _print_results(results):
    """Print results of Workflow.filter"""
    for item, score, rule in results:
        print(('{!r} (rule {}) : {}'.format(item[0], rule, score)))


def test_filter_all_rules(wf):
    """Filter: all rules"""
    results = wf.filter('test', SEARCH_ITEMS, key=lambda x: x[0],
                        ascending=True, match_on=MATCH_ALL)
    assert len(results) == 8
    # now with scores, rules
    results = wf.filter('test', SEARCH_ITEMS, key=lambda x: x[0],
                        include_score=True, match_on=MATCH_ALL)
    assert len(results) == 8
    for item, score, rule in results:
        wf.logger.debug('%s : %s', item, score)
        for value, r in SEARCH_ITEMS:
            if value == item[0]:
                assert rule == r
    # self.assertTrue(False)


def test_filter_no_caps(wf):
    """Filter: no caps"""
    results = wf.filter('test', SEARCH_ITEMS, key=lambda x: x[0],
                        ascending=True,
                        match_on=MATCH_ALL ^ MATCH_CAPITALS,
                        include_score=True)
    _print_results(results)
    for _, _, rule in results:
        assert rule != MATCH_CAPITALS
    # assert len(results) == 7


def test_filter_only_caps(wf):
    """Filter: only caps"""
    results = wf.filter('test', SEARCH_ITEMS, key=lambda x: x[0],
                        ascending=True,
                        match_on=MATCH_CAPITALS,
                        include_score=True)
    _print_results(results)
    assert len(results) == 1


def test_filter_max_results(wf):
    """Filter: max results"""
    results = wf.filter('test', SEARCH_ITEMS, key=lambda x: x[0],
                        ascending=True, max_results=4)
    assert len(results) == 4


def test_filter_min_score(wf):
    """Filter: min score"""
    results = wf.filter('test', SEARCH_ITEMS, key=lambda x: x[0],
                        ascending=True, min_score=90,
                        include_score=True)
    assert len(results) == 6


def test_filter_folding(wf):
    """Filter: diacritic folding"""
    for key, query in SEARCH_ITEMS_DIACRITICS:
        results = wf.filter(query, [key], min_score=90,
                            include_score=True)
        assert len(results) == 1


def test_filter_no_folding(wf):
    """Filter: folding turned off for non-ASCII query"""
    data = ['fühler', 'fuhler', 'fübar', 'fubar']
    results = wf.filter('fü', data)
    assert len(results) == 2


@pytest.mark.parametrize('key,query', SEARCH_ITEMS_DIACRITICS)
def test_filter_folding_off(wf, key, query):
    """Filter: diacritic folding off"""
    results = wf.filter(query, [key], min_score=90,
                        include_score=True,
                        fold_diacritics=False)
    assert len(results) == 0


@pytest.mark.parametrize('key,query', SEARCH_ITEMS_DIACRITICS)
def test_filter_folding_force_on(wf, key, query):
    """Filter: diacritic folding forced on"""
    wf.settings['__workflow_diacritic_folding'] = True
    results = wf.filter(query, [key], min_score=90,
                        include_score=True,
                        fold_diacritics=False)
    assert len(results) == 1, f'expected q={query} over "{key}" to find one result'


@pytest.mark.parametrize('key,query', SEARCH_ITEMS_DIACRITICS)
def test_filter_folding_force_off(wf, key, query):
    """Filter: diacritic folding forced off"""
    wf.settings['__workflow_diacritic_folding'] = False
    results = wf.filter(query, [key], min_score=90,
                        include_score=True)
    assert len(results) == 0


def test_filter_empty_key(wf):
    """Filter: empty keys are ignored"""
    data = ['bob', 'sue', 'henry']

    def key(s):
        """Return empty key"""
        return ''

    results = wf.filter('lager', data, key)
    assert len(results) == 0


def test_filter_empty_query_words(wf):
    """Filter: empty query returns all results"""
    data = ['bob', 'sue', 'henry']
    assert wf.filter('   ', data) == data
    assert wf.filter('', data) == data


def test_filter_empty_query_words_ignored(wf):
    """Filter: empty query words ignored"""
    data = ['bob jones', 'sue smith', 'henry rogers']
    results = wf.filter('bob       jones', data)
    assert len(results) == 1


def test_filter_identical_items(wf):
    """Filter: identical items are not discarded"""
    data = ['bob', 'bob', 'bob']
    results = wf.filter('bob', data)
    assert len(results) == len(data)


def test_filter_reversed_results(wf):
    """Filter: results reversed"""
    data = ['bob', 'bobby', 'bobby smith']
    results = wf.filter('bob', data)
    assert results == data
    results = wf.filter('bob', data, ascending=True)
    assert results == data[::-1]


def test_punctuation(wf):
    """Punctuation: dumbified"""
    for input, output in PUNCTUATION_DATA:
        assert wf.dumbify_punctuation(input) == output


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
