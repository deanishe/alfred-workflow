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

import os

__version__ = open(os.path.join(os.path.dirname(__file__), 'version')).read()


# Workflow objects
from .workflow import Workflow, manager

# Exceptions
from .workflow import PasswordNotFound, KeychainError

# Icons
from .workflow import (ICON_ERROR, ICON_WARNING, ICON_NOTE, ICON_INFO,
                       ICON_FAVORITE, ICON_FAVOURITE, ICON_USER, ICON_GROUP,
                       ICON_HELP, ICON_NETWORK, ICON_WEB, ICON_COLOR,
                       ICON_COLOUR, ICON_SYNC, ICON_SETTINGS, ICON_TRASH,
                       ICON_MUSIC, ICON_BURN, ICON_ACCOUNT, ICON_ERROR)

# Filter matching rules
from .workflow import (MATCH_ALL, MATCH_ALLCHARS, MATCH_ATOM,
                       MATCH_CAPITALS, MATCH_INITIALS,
                       MATCH_INITIALS_CONTAIN, MATCH_INITIALS_STARTSWITH,
                       MATCH_STARTSWITH, MATCH_SUBSTRING)
