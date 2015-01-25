#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""
A Python helper library for `Alfred 2 <http://www.alfredapp.com/>`_ Workflow
authors.
"""

from __future__ import print_function, unicode_literals, absolute_import

import os

__title__ = 'Alfred-Workflow'
__version__ = open(os.path.join(os.path.dirname(__file__), 'version')).read()
__author__ = 'Dean Jackson'
__licence__ = 'MIT'
__copyright__ = 'Copyright 2015 Dean Jackson'
__url__ = 'http://www.deanishe.net/alfred-workflow'


# Workflow objects
from .workflow import Workflow, manager

# Exceptions
from .base import PasswordNotFound, KeychainError

# Icons
from .icons import (
    ACCOUNT as ICON_ACCOUNT,
    BURN as ICON_BURN,
    CLOCK as ICON_CLOCK,
    COLOR as ICON_COLOR,
    COLOUR as ICON_COLOUR,
    EJECT as ICON_EJECT,
    ERROR as ICON_ERROR,
    FAVORITE as ICON_FAVORITE,
    FAVOURITE as ICON_FAVOURITE,
    GROUP as ICON_GROUP,
    HELP as ICON_HELP,
    HOME as ICON_HOME,
    INFO as ICON_INFO,
    NETWORK as ICON_NETWORK,
    NOTE as ICON_NOTE,
    SETTINGS as ICON_SETTINGS,
    SWIRL as ICON_SWIRL,
    SWITCH as ICON_SWITCH,
    SYNC as ICON_SYNC,
    TRASH as ICON_TRASH,
    USER as ICON_USER,
    WARNING as ICON_WARNING,
    WEB as ICON_WEB,
)

# Filter matching rules
from .search import (
    MATCH_ALL,
    MATCH_ALLCHARS,
    MATCH_ATOM,
    MATCH_CAPITALS,
    MATCH_INITIALS,
    MATCH_INITIALS_CONTAIN,
    MATCH_INITIALS_STARTSWITH,
    MATCH_STARTSWITH,
    MATCH_SUBSTRING,
)

__all__ = [
    'Workflow',
    'manager',
    'PasswordNotFound',
    'KeychainError',
    'ICON_ACCOUNT',
    'ICON_BURN',
    'ICON_CLOCK',
    'ICON_COLOR',
    'ICON_COLOUR',
    'ICON_EJECT',
    'ICON_ERROR',
    'ICON_FAVORITE',
    'ICON_FAVOURITE',
    'ICON_GROUP',
    'ICON_HELP',
    'ICON_HOME',
    'ICON_INFO',
    'ICON_NETWORK',
    'ICON_NOTE',
    'ICON_SETTINGS',
    'ICON_SWIRL',
    'ICON_SWITCH',
    'ICON_SYNC',
    'ICON_TRASH',
    'ICON_USER',
    'ICON_WARNING',
    'ICON_WEB',
    'MATCH_ALL',
    'MATCH_ALLCHARS',
    'MATCH_ATOM',
    'MATCH_CAPITALS',
    'MATCH_INITIALS',
    'MATCH_INITIALS_CONTAIN',
    'MATCH_INITIALS_STARTSWITH',
    'MATCH_STARTSWITH',
    'MATCH_SUBSTRING',
]
