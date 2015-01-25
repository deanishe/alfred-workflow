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
These icons are default OS X icons. They are super-high quality, and
will be familiar to users.
This library uses `ERROR` when a workflow dies in flames, so
in my own workflows, I use `WARNING` for less fatal errors
(e.g. bad user input, no results etc.)

The system icons are all in this directory. There are many more than
are listed here.

"""


from __future__ import print_function, unicode_literals, absolute_import

from os.path import join

####################################################################
# Standard system icons
####################################################################

ROOTDIR = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources'

ACCOUNT = join(ROOTDIR, 'Accounts.icns')
BURN = join(ROOTDIR, 'BurningIcon.icns')
CLOCK = join(ROOTDIR, 'Clock.icns')
COLOR = join(ROOTDIR, 'ProfileBackgroundColor.icns')
EJECT = join(ROOTDIR, 'EjectMediaIcon.icns')
# Shown when a workflow throws an error
ERROR = join(ROOTDIR, 'AlertStopIcon.icns')
FAVORITE = join(ROOTDIR, 'ToolbarFavoritesIcon.icns')
GROUP = join(ROOTDIR, 'GroupIcon.icns')
HELP = join(ROOTDIR, 'HelpIcon.icns')
HOME = join(ROOTDIR, 'HomeFolderIcon.icns')
INFO = join(ROOTDIR, 'ToolbarInfo.icns')
NETWORK = join(ROOTDIR, 'GenericNetworkIcon.icns')
NOTE = join(ROOTDIR, 'AlertNoteIcon.icns')
SETTINGS = join(ROOTDIR, 'ToolbarAdvanced.icns')
SWIRL = join(ROOTDIR, 'ErasingIcon.icns')
SWITCH = join(ROOTDIR, 'General.icns')
SYNC = join(ROOTDIR, 'Sync.icns')
TRASH = join(ROOTDIR, 'TrashIcon.icns')
USER = join(ROOTDIR, 'UserIcon.icns')
WARNING = join(ROOTDIR, 'AlertCautionIcon.icns')
WEB = join(ROOTDIR, 'BookmarkIcon.icns')
# Queen's English, if you please
COLOUR = COLOR
FAVOURITE = FAVORITE
