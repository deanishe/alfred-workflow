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

import re
import string
import unicodedata

####################################################################
# non-ASCII to ASCII diacritic folding.
# Used by `fold_to_ascii` method
####################################################################

ASCII_REPLACEMENTS = {
    '\u0410': 'A', '\u0395': 'E', '\u0418': 'I', '\u039d': 'N',
    '\u0420': 'R', '\u03a5': 'U', '\u1d26': 'G', '\u0428': 'Sh',
    '\u0430': 'a', '\u03b5': 'e', '\u0438': 'i', '\u03bd': 'n',
    '\u0440': 'r', '\xc3': 'A', '\u03c5': 'u', '\u0146': 'n',
    '\u0448': 'sh', '\xcb': 'E', '\u014e': 'O', '\xd3': 'O',
    '\u0156': 'R', '\xdb': 'U', '\u015e': 'S', '\xe3': 'a',
    '\u0166': 'T', '\xeb': 'e', '\u016e': 'U', '\xf3': 'o',
    '\u0176': 'Y', '\xfb': 'u', '\u017e': 'z', '\u0413': 'G',
    '\u0392': 'B', '\u041b': 'L', '\u039a': 'K', '\u0423': 'U',
    '\u1d29': 'R', '\u042b': 'Y', '\u0433': 'g', '\u03b2': 'b',
    '\u043b': 'l', '\u03ba': 'k', '\u0141': 'L', '\xc0': 'A',
    '\u0443': 'u', '\u03c2': 's', '\xc8': 'E', '\u044b': 'y',
    '\u0151': 'o', '\xd0': 'D', '\u0159': 'r', '\xd8': 'O',
    '\u0161': 's', '\xe0': 'a', '\u0169': 'u', '\xe8': 'e',
    '\u0171': 'u', '\xf0': 'd', '\u1ef4': 'Y', '\u0179': 'Z',
    '\xf8': 'o', '\u0397': 'E', '\u0416': 'Zh', '\u039f': 'O',
    '\u041e': 'O', '\u03a7': 'Kh', '\u0426': 'Ts', '\u1d28': 'P',
    '\u042e': 'Iu', '\u03b7': 'e', '\u0436': 'zh', '\u03bf': 'o',
    '\u043e': 'o', '\xc1': 'A', '\u03c7': 'kh', '\u0446': 'ts',
    '\xc9': 'E', '\u0148': 'n', '\u044e': 'iu', '\xd1': 'N',
    '\u0150': 'O', '\xd9': 'U', '\u0158': 'R', '\xe1': 'a',
    '\u0160': 'S', '\xe9': 'e', '\u0168': 'U', '\xf1': 'n',
    '\u0170': 'U', '\u1ef5': 'y', '\xf9': 'u', '\u0178': 'Y',
    '\u0411': 'B', '\u0394': 'D', '\u0419': 'I', '\u039c': 'M',
    '\u0421': 'S', '\u03a4': 'T', '\u0429': 'Shch', '\u0431': 'b',
    '\u03b4': 'd', '\u0439': 'i', '\u03bc': 'm', '\u0441': 's',
    '\u0143': 'N', '\u03c4': 't', '\xc6': 'AE', '\u0449': 'shch',
    '\u014b': 'NG', '\xce': 'I', '\u0153': 'oe', '\xd6': 'O',
    '\u015b': 's', '\xde': 'Th', '\u0163': 't', '\xe6': 'ae',
    '\u016b': 'u', '\xee': 'i', '\u1ef2': 'Y', '\xf6': 'o',
    '\u017b': 'Z', '\xfe': 'th', '\u0391': 'A', '\u0414': 'D',
    '\u0399': 'I', '\u041c': 'M', '\u03a1': 'R', '\u0424': 'F',
    '\u03a9': 'O', '\u1d2a': 'PS', '\u042c': "'", '\u03b1': 'a',
    '\u0434': 'd', '\u03b9': 'i', '\u043c': 'm', '\u03c1': 'r',
    '\u0142': 'l', '\u0444': 'f', '\xc7': 'C', '\u03c9': 'o',
    '\u014a': 'ng', '\u044c': "'", '\xcf': 'I', '\u0152': 'OE',
    '\u015a': 'S', '\xdf': 'ss', '\u0162': 'T', '\xe7': 'c',
    '\u016a': 'U', '\xef': 'i', '\u1ef3': 'y', '\u017a': 'z',
    '\xff': 'y', '\u0417': 'Z', '\u0396': 'Z', '\u041f': 'P',
    '\u039e': 'Ks', '\u0427': 'Ch', '\u03a6': 'Ph', '\u042f': 'Ia',
    '\u0437': 'z', '\u03b6': 'z', '\u043f': 'p', '\u03be': 'x',
    '\u0145': 'N', '\xc4': 'A', '\u0447': 'ch', '\u03c6': 'ph',
    '\u014d': 'o', '\xcc': 'I', '\u044f': 'ia', '\u0155': 'r',
    '\xd4': 'O', '\u015d': 's', '\xdc': 'U', '\u0165': 't',
    '\xe4': 'a', '\u016d': 'u', '\xec': 'i', '\u0175': 'w',
    '\xf4': 'o', '\u1ef8': 'Y', '\u017d': 'Z', '\xfc': 'u',
    '\u0393': 'G', '\u0412': 'V', '\u039b': 'L', '\u041a': 'K',
    '\u03a3': 'S', '\u0422': 'T', '\u042a': "'", '\u03b3': 'g',
    '\u0432': 'v', '\u03bb': 'l', '\u043a': 'k', '\u03c3': 's',
    '\u0442': 't', '\xc5': 'A', '\u0144': 'n', '\u044a': "'",
    '\xcd': 'I', '\u014c': 'O', '\xd5': 'O', '\u0154': 'R',
    '\xdd': 'Y', '\u015c': 'S', '\xe5': 'a', '\u0164': 'T',
    '\xed': 'i', '\u016c': 'U', '\xf5': 'o', '\u0174': 'W',
    '\u1ef9': 'y', '\xfd': 'y', '\u017c': 'z', '\u0415': 'E',
    '\u0398': 'Th', '\u041d': 'N', '\u1e9e': 'Ss', '\u03a0': 'P',
    '\u0425': 'Kh', '\u1d27': 'L', '\u03a8': 'Ps', '\u042d': 'E',
    '\u0435': 'e', '\u03b8': 'th', '\u043d': 'n', '\u03c0': 'p',
    '\xc2': 'A', '\u0445': 'kh', '\u0147': 'N', '\u03c8': 'ps',
    '\xca': 'E', '\u044d': 'e', '\u014f': 'o', '\xd2': 'O',
    '\u0157': 'r', '\xda': 'U', '\u015f': 's', '\xe2': 'a',
    '\u0167': 't', '\xea': 'e', '\u016f': 'u', '\xf2': 'o',
    '\u0177': 'y', '\xfa': 'u', '\u017f': 's',
}

####################################################################
# Smart-to-dumb punctuation mapping
####################################################################

DUMB_PUNCTUATION = {
    '‘': "'",
    '’': "'",
    '‚': "'",
    '“': '"',
    '”': '"',
    '„': '"',
    '–': '-',
    '—': '-'
}

####################################################################
# Used by `Workflow.filter`
####################################################################

# Anchor characters in a name
#: Characters that indicate the beginning of a "word" in CamelCase
INITIALS = string.ascii_uppercase + string.digits

#: Split on non-letters, numbers
split_on_delimiters = re.compile('[^a-zA-Z0-9]').split

# Match filter flags
#: Match items that start with ``query``
MATCH_STARTSWITH = 1
#: Match items whose capital letters start with ``query``
MATCH_CAPITALS = 2
#: Match items with a component "word" that matches ``query``
MATCH_ATOM = 4
#: Match items whose initials (based on atoms) start with ``query``
MATCH_INITIALS_STARTSWITH = 8
#: Match items whose initials (based on atoms) contain ``query``
MATCH_INITIALS_CONTAIN = 16
#: Combination of :const:`MATCH_INITIALS_STARTSWITH` and
#: :const:`MATCH_INITIALS_CONTAIN`
MATCH_INITIALS = 24
#: Match items if ``query`` is a substring
MATCH_SUBSTRING = 32
#: Match items if all characters in ``query`` appear in the item in order
MATCH_ALLCHARS = 64
#: Combination of all other ``MATCH_*`` constants
MATCH_ALL = 127

# Cache for compiled regular expressions
_search_pattern_cache = {}


def isascii(text):
    """Test if ``text`` contains only ASCII characters

    :param text: text to test for ASCII-ness
    :type text: ``unicode``
    :returns: ``True`` if ``text`` contains only ASCII characters
    :rtype: ``Boolean``
    """

    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True


def fold_to_ascii(text):
    """Convert non-ASCII characters to closest ASCII equivalent.

    .. versionadded:: 1.3

    .. note:: This only works for a subset of European languages.

    :param text: text to convert
    :type text: ``unicode``
    :returns: text containing only ASCII characters
    :rtype: ``unicode``

    """
    if isascii(text):
        return text
    text = ''.join([ASCII_REPLACEMENTS.get(c, c) for c in text])
    return unicode(unicodedata.normalize('NFKD',
                   text).encode('ascii', 'ignore'))


def dumbify_punctuation(text):
    """Convert non-ASCII punctuation to closest ASCII equivalent.

    This method replaces "smart" quotes and n- or m-dashes with their
    workaday ASCII equivalents. This method is currently not used
    internally, but exists as a helper method for workflow authors.

    .. versionadded: 1.9.7

    :param text: text to convert
    :type text: ``unicode``
    :returns: text with only ASCII punctuation
    :rtype: ``unicode``

    """
    if isascii(text):
        return text

    text = ''.join([DUMB_PUNCTUATION.get(c, c) for c in text])
    return text


def filter(query, items, key=lambda x: x, ascending=False,
           include_score=False, min_score=0, max_results=0,
           match_on=MATCH_ALL, fold_diacritics=True):
    """Fuzzy search filter. Returns list of ``items`` that match ``query``.

    ``query`` is case-insensitive. Any item that does not contain the
    entirety of ``query`` is rejected.

    .. warning::

        If ``query`` is an empty string or contains only whitespace,
        a :class:`ValueError` will be raised.

    :param query: query to test items against
    :type query: ``unicode``
    :param items: iterable of items to test
    :type items: ``list`` or ``tuple``
    :param key: function to get comparison key from ``items``.
        Must return a ``unicode`` string. The default simply returns
        the item.
    :type key: ``callable``
    :param ascending: set to ``True`` to get worst matches first
    :type ascending: ``Boolean``
    :param include_score: Useful for debugging the scoring algorithm.
        If ``True``, results will be a list of tuples
        ``(item, score, rule)``.
    :type include_score: ``Boolean``
    :param min_score: If non-zero, ignore results with a score lower
        than this.
    :type min_score: ``int``
    :param max_results: If non-zero, prune results list to this length.
    :type max_results: ``int``
    :param match_on: Filter option flags. Bitwise-combined list of
        ``MATCH_*`` constants (see below).
    :type match_on: ``int``
    :param fold_diacritics: Convert search keys to ASCII-only
        characters if ``query`` only contains ASCII characters.
    :type fold_diacritics: ``Boolean``
    :returns: list of ``items`` matching ``query`` or list of
        ``(item, score, rule)`` `tuples` if ``include_score`` is ``True``.
        ``rule`` is the ``MATCH_*`` rule that matched the item.
    :rtype: ``list``

    **Matching rules**

    By default, :meth:`filter` uses all of the following flags (i.e.
    :const:`MATCH_ALL`). The tests are always run in the given order:

    1. :const:`MATCH_STARTSWITH` : Item search key startswith
        ``query``(case-insensitive).
    2. :const:`MATCH_CAPITALS` : The list of capital letters in item
        search key starts with ``query`` (``query`` may be
        lower-case). E.g., ``of`` would match ``OmniFocus``,
        ``gc`` would match ``Google Chrome``
    3. :const:`MATCH_ATOM` : Search key is split into "atoms" on
        non-word characters (.,-,' etc.). Matches if ``query`` is
        one of these atoms (case-insensitive).
    4. :const:`MATCH_INITIALS_STARTSWITH` : Initials are the first
        characters of the above-described "atoms" (case-insensitive).
    5. :const:`MATCH_INITIALS_CONTAIN` : ``query`` is a substring of
        the above-described initials.
    6. :const:`MATCH_INITIALS` : Combination of (4) and (5).
    7. :const:`MATCH_SUBSTRING` : Match if ``query`` is a substring
        of item search key (case-insensitive).
    8. :const:`MATCH_ALLCHARS` : Matches if all characters in
        ``query`` appear in item search key in the same order
        (case-insensitive).
    9. :const:`MATCH_ALL` : Combination of all the above.


    :const:`MATCH_ALLCHARS` is considerably slower than the other
    tests and provides much less accurate results.

    **Examples:**

    To ignore :const:`MATCH_ALLCHARS` (tends to provide the worst
    matches and is expensive to run), use
    ``match_on=MATCH_ALL ^ MATCH_ALLCHARS``.

    To match only on capitals, use ``match_on=MATCH_CAPITALS``.

    To match only on startswith and substring, use
    ``match_on=MATCH_STARTSWITH | MATCH_SUBSTRING``.

    **Diacritic folding**

    .. versionadded:: 1.3

    If ``fold_diacritics`` is ``True`` (the default), and ``query``
    contains only ASCII characters, non-ASCII characters in search keys
    will be converted to ASCII equivalents (e.g. **ü** -> **u**,
    **ß** -> **ss**, **é** -> **e**).

    See :const:`ASCII_REPLACEMENTS` for all replacements.

    If ``query`` contains non-ASCII characters, search keys will not be
    altered.

    """

    if not query:
        raise ValueError('Empty `query`')

    # Remove preceding/trailing spaces
    query = query.strip()

    if not query:
        raise ValueError('`query` contains only whitespace')

    # Use user override if there is one
    # fold_diacritics = self.settings.get(base.KEY_DIACRITICS,
    #                                     fold_diacritics)

    results = []

    for item in items:
        skip = False
        score = 0
        words = [s.strip() for s in query.split(' ')]
        value = key(item).strip()
        if value == '':
            continue
        for word in words:
            if word == '':
                continue
            s, rule = _filter_item(value, word, match_on, fold_diacritics)

            if not s:  # Skip items that don't match part of the query
                skip = True
            score += s

        if skip:
            continue

        if score:
            # use "reversed" `score` (i.e. highest becomes lowest) and
            # `value` as sort key. This means items with the same score
            # will be sorted in alphabetical not reverse alphabetical order
            results.append(((100.0 / score, value.lower(), score),
                            (item, score, rule)))

    # sort on keys, then discard the keys
    results.sort(reverse=ascending)
    results = [t[1] for t in results]

    if min_score:
        results = [r for r in results if r[1] > min_score]

    if max_results and len(results) > max_results:
        results = results[:max_results]

    # return list of ``(item, score, rule)``
    if include_score:
        return results
    # just return list of items
    return [t[0] for t in results]


def _filter_item(value, query, match_on, fold_diacritics):
    """Filter ``value`` against ``query`` using rules ``match_on``

    :returns: ``(score, rule)``

    """

    query = query.lower()

    if not isascii(query):
        fold_diacritics = False

    if fold_diacritics:
        value = fold_to_ascii(value)

    # pre-filter any items that do not contain all characters
    # of ``query`` to save on running several more expensive tests
    if not set(query) <= set(value.lower()):

        return (0, None)

    # item starts with query
    if match_on & MATCH_STARTSWITH and value.lower().startswith(query):
        score = 100.0 - (len(value) / len(query))

        return (score, MATCH_STARTSWITH)

    # query matches capitalised letters in item,
    # e.g. of = OmniFocus
    if match_on & MATCH_CAPITALS:
        initials = ''.join([c for c in value if c in INITIALS])
        if initials.lower().startswith(query):
            score = 100.0 - (len(initials) / len(query))

            return (score, MATCH_CAPITALS)

    # split the item into "atoms", i.e. words separated by
    # spaces or other non-word characters
    if (match_on & MATCH_ATOM or
            match_on & MATCH_INITIALS_CONTAIN or
            match_on & MATCH_INITIALS_STARTSWITH):
        atoms = [s.lower() for s in split_on_delimiters(value)]
        # print('atoms : %s  -->  %s' % (value, atoms))
        # initials of the atoms
        initials = ''.join([s[0] for s in atoms if s])

    if match_on & MATCH_ATOM:
        # is `query` one of the atoms in item?
        # similar to substring, but scores more highly, as it's
        # a word within the item
        if query in atoms:
            score = 100.0 - (len(value) / len(query))

            return (score, MATCH_ATOM)

    # `query` matches start (or all) of the initials of the
    # atoms, e.g. ``himym`` matches "How I Met Your Mother"
    # *and* "how i met your mother" (the ``capitals`` rule only
    # matches the former)
    if (match_on & MATCH_INITIALS_STARTSWITH and
            initials.startswith(query)):
        score = 100.0 - (len(initials) / len(query))

        return (score, MATCH_INITIALS_STARTSWITH)

    # `query` is a substring of initials, e.g. ``doh`` matches
    # "The Dukes of Hazzard"
    elif (match_on & MATCH_INITIALS_CONTAIN and
            query in initials):
        score = 95.0 - (len(initials) / len(query))

        return (score, MATCH_INITIALS_CONTAIN)

    # `query` is a substring of item
    if match_on & MATCH_SUBSTRING and query in value.lower():
        score = 90.0 - (len(value) / len(query))

        return (score, MATCH_SUBSTRING)

    # finally, assign a score based on how close together the
    # characters in `query` are in item.
    if match_on & MATCH_ALLCHARS:
        search = _search_for_query(query)
        match = search(value)
        if match:
            score = 100.0 / ((1 + match.start()) *
                             (match.end() - match.start() + 1))

            return (score, MATCH_ALLCHARS)

    # Nothing matched
    return (0, None)


def _search_for_query(query):
    global _search_pattern_cache
    if query in _search_pattern_cache:
        return _search_pattern_cache[query]

    # Build pattern: include all characters
    pattern = []
    for c in query:
        # pattern.append('[^{0}]*{0}'.format(re.escape(c)))
        pattern.append('.*?{0}'.format(re.escape(c)))
    pattern = ''.join(pattern)
    search = re.compile(pattern, re.IGNORECASE).search

    _search_pattern_cache[query] = search
    return search
