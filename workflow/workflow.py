# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""
Helper class for Alfred 2 workflow authors.

Basic usage
-----------

Copy the ``workflow`` directory into the root directory of your workflow::

    Your Workflow/
        info.plist
        icon.png
        workflow/
            __init__.py
            workflow.py
            web.py
        yourscript.py
        etc.

In Alfred, make sure your Script Filter is set to select ``/bin/bash`` as
the **Language**, and select the following (and only the following)
**Escaping** options:

- Backquotes
- Double Quotes
- Dollars
- Backslashes

The **Script** field should contain the following::

    python yourscript.py "{query}"


where ``yourscript.py`` is the name of your script.

Your workflow should start out like this. This enables :class:`Workflow`
to capture any errors thrown by your scripts::

    #!/usr/bin/python
    # encoding: utf-8

    import sys

    from workflow import Workflow


    def main(wf):
        # The Workflow instance will be passed to the function
        # you call from `Workflow.run`
        # Your imports here if you want to catch import errors
        import somemodule
        import anothermodule
        # Get args from Workflow, already in normalised Unicode
        args = wf.args

        # Do stuff here ...

        # Add an item to Alfred feedback
        wf.add_item(u'Item title', u'Item subtitle')

        # Send output to Alfred
        wf.send_feedback()


    if __name__ == '__main__':
        wf = Workflow()
        sys.exit(wf.run(main))

"""

from __future__ import print_function, unicode_literals

import os
import sys
import string
import re
import plistlib
import subprocess
import unicodedata
import shutil
import json
import pickle
import time
import logging
import logging.handlers
try:
    import xml.etree.cElementTree as ET
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as ET


####################################################################
# Some standard system icons
####################################################################

# Shown when a workflow throws an error
ICON_ERROR = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/AlertStopIcon.icns')
ICON_WARNING = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/AlertCautionIcon.icns')
ICON_NOTE = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/AlertNoteIcon.icns')
ICON_INFO = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/ToolbarInfo.icns')
ICON_FAVORITE = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                 '/Resources/ToolbarFavoritesIcon.icns')
ICON_FAVOURITE = ICON_FAVORITE  # Queen's English, if you please
ICON_USER = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/UserIcon.icns')
ICON_GROUP = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/GroupIcon.icns')
ICON_HELP = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/HelpIcon.icns')
ICON_NETWORK = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/GenericNetworkIcon.icns')
ICON_WEB = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
            '/Resources/BookmarkIcon.icns')
ICON_COLOR = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/ProfileBackgroundColor.icns')
ICON_COLOUR = ICON_COLOR
ICON_SYNC = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/Sync.icns')
ICON_SETTINGS = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                 '/Resources/ToolbarAdvanced.icns')
ICON_TRASH = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/TrashIcon.icns')
ICON_MUSIC = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/ToolbarMusicFolderIcon.icns')
ICON_BURN = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/BurningIcon.icns')
ICON_ACCOUNT = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/Accounts.icns')


####################################################################
# Used by `Workflow.filter`
####################################################################

# Anchor characters in a name
INITIALS = string.ascii_uppercase + string.digits

# Split on non-letters, numbers
split_on_delimiters = re.compile('[^a-zA-Z0-9]').split


####################################################################
# Keychain access errors
####################################################################

class KeychainError(Exception):
    pass


class PasswordNotFound(KeychainError):
    pass


class PasswordExists(KeychainError):
    pass


####################################################################
# Implementation classes
####################################################################

class Item(object):
    """A feedback item for Alfred.

    You probably shouldn't use this class directly, but via
    :class:`Workflow.add_item`.

    """

    def __init__(self, title, subtitle='', arg=None, autocomplete=None,
                 valid=False, uid=None, icon=None, icontype=None,
                 type=None):
        """Arguments the same as for :class:`Workflow.add_item`.

        """

        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.autocomplete = autocomplete
        self.valid = valid
        self.uid = uid
        self.icon = icon
        self.icontype = icontype
        self.type = type

    @property
    def elem(self):
        """Return item as XML element for Alfred

        :returns: :class:`~xml.etree.ElementTree.Element` instance
                  for :class:`Item`

        """

        attr = {}
        if self.valid:
            attr['valid'] = 'yes'
        else:
            attr['valid'] = 'no'
        # Optional attributes
        for name in ('uid', 'type', 'autocomplete'):
            value = getattr(self, name, None)
            if value:
                attr[name] = value

        root = ET.Element('item', attr)
        ET.SubElement(root, 'title').text = self.title
        ET.SubElement(root, 'subtitle').text = self.subtitle
        if self.arg:
            ET.SubElement(root, 'arg').text = self.arg
        # Add icon if there is one
        if self.icon:
            if self.icontype:
                attr = dict(type=self.icontype)
            else:
                attr = {}
            ET.SubElement(root, 'icon', attr).text = self.icon
        return root


class Settings(dict):
    """A dictionary that saves itself when changed.

    An appropriate instance is provided by `Workflow` instances at
    `Workflow.settings`.

    """

    def __init__(self, filepath, defaults=None):
        """Dictionary keys & values will be saved as a JSON file
        at `filepath`. If the file does not exist, the dictionary
        (and settings file) will be initialised with `defaults`.

        :param filepath: where to save the settings
        :type filepath: `unicode`
        :param defaults: dict of default settings
        :type defaults: `dict`

        """

        super(Settings, self).__init__()
        self._filepath = filepath
        self._nosave = False
        if not os.path.exists(self._filepath) and defaults:
            for key, val in defaults.items():
                self[key] = val
            self._save()  # save default settings
        else:
            self._load()

    def _load(self):
        """Load cached settings from JSON file `self._filepath`"""

        self._nosave = True
        with open(self._filepath, 'rb') as file:
            for key, value in json.load(file, encoding='utf-8').items():
                self[key] = value
        self._nosave = False

    def _save(self):
        """Save settings to JSON file `self._filepath`"""
        if self._nosave:
            return
        data = {}
        for key, value in self.items():
            data[key] = value
        with open(self._filepath, 'wb') as file:
            json.dump(data, file, sort_keys=True, indent=2, encoding='utf-8')

    # dict methods
    def __setitem__(self, key, value):
        super(Settings, self).__setitem__(key, value)
        self._save()

    def update(self, *args, **kwargs):
        super(Settings, self).update(*args, **kwargs)
        self._save()

    def setdefault(self, key, value=None):
        super(Settings, self).setdefault(key, value)
        self._save()


class Workflow(object):
    """Create new :class:`Workflow` instance.

        :param default_settings: default workflow settings. If no settings file
            exists, :class:`Workflow.settings` will be pre-populated with
            ``default_settings``.
        :type default_settings: :class:`dict`
        :param input_encoding: encoding of command line arguments
        :type input_encoding: :class:`unicode`
        :param normalization: normalisation to apply to CLI args.
            Use ``NFC`` for Python, ``NFD`` if working with data
            from the filesystem.
        :type normalization: :class:`unicode`
        :param capture_args: capture and act on ``workflow:*`` arguments
        :type capture_args: :class:`Boolean`
        :param libraries: sequence of paths to directories containing
                          libraries. These paths will be prepended to `sys.path`.
        :type libraries: :class:`tuple` or :class:`list`

    """

    # Which class to use to generate feedback items. You probably
    # won't want to change this
    item_class = Item

    def __init__(self, default_settings=None, input_encoding='utf-8',
                 normalization='NFC', capture_args=True, libraries=None):

        self._default_settings = default_settings or {}
        self._input_encoding = input_encoding
        self._normalizsation = normalization
        self._capture_args = capture_args
        self._settings_path = None
        self._settings = None
        self._bundleid = None
        self._name = None
        # info.plist should be in the directory above this one
        self._info_plist = os.path.join(os.path.dirname(
                                        os.path.dirname(__file__)),
                                        'info.plist')
        self._info = None
        self._info_loaded = False
        self._logger = None
        self._items = []
        if libraries:
            sys.path = libraries + sys.path

    ####################################################################
    # API methods
    ####################################################################

    # info.plist contents ----------------------------------------------

    @property
    def info(self):
        """`dict` of ``info.plist`` contents

        :returns: `dict`

        """

        if not self._info_loaded:
            self._load_info_plist()
        return self._info

    @property
    def bundleid(self):
        """Workflow bundle ID from ``info.plist``

        :returns: bundle ID
        :rtype: `unicode`

        """

        if not self._bundleid:
            self._bundleid = unicode(self.info['bundleid'], 'utf-8')
        return self._bundleid

    @property
    def name(self):
        """Workflow name from ``info.plist``

        :returns: workflow name
        :rtype: `unicode`

        """

        if not self._name:
            self._name = unicode(self.info['name'], 'utf-8')
        return self._name

    # Workflow utility methods -----------------------------------------

    @property
    def args(self):
        """Return command line args as normalised unicode

        If `self._capture_args` is True, `Workflow` will interpret "capture"
        the argument 'workflow:openlog' and open the log file.

        """

        msg = None
        args = [self.decode(arg) for arg in sys.argv[1:]]
        if len(args) and self._capture_args:
            if 'workflow:openlog' in args:
                self.openlog()
                msg = 'Opening workflow log file'
            elif 'workflow:delcache' in args:
                self.clear_cache()
                msg = 'Deleted workflow cache'
            elif 'workflow:delsettings' in args:
                self.clear_settings()
                msg = 'Deleted workflow settings'
            if msg:
                self.logger.info(msg)
                if not sys.stdout.isatty():  # Show message in Alfred
                    self.add_item(msg, valid=False, icon=ICON_INFO)
                    self.send_feedback()
                sys.exit(0)
        return args

    @property
    def cachedir(self):
        """Path to workflow's cache directory

        :returns: full path to workflow's cache directory
        :rtype: `unicode`

        """

        dirpath = os.path.join(os.path.expanduser(
            '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/'),
            self.bundleid)
        return self._create(dirpath)

    @property
    def datadir(self):
        """Path to workflow's data directory

        :returns: full path to workflow data directory
        :rtype: `unicode`

        """

        dirpath = os.path.join(os.path.expanduser(
            '~/Library/Application Support/Alfred 2/Workflow Data/'),
            self.bundleid)
        return self._create(dirpath)

    def cachefile(self, filename):
        """Return full path to ``filename`` in workflow's cache dir

        :param filename: basename of file
        :type filename: `unicode`
        :returns: full path to file within cache directory
        :rtype: `unicode`

        """

        return os.path.join(self.cachedir, filename)

    def datafile(self, filename):
        """Return full path to ``filename`` in workflow's data dir

        :param filename: basename of file
        :type filename: `unicode`
        :returns: full path to file within data directory
        :rtype: `unicode`

        """

        return os.path.join(self.datadir, filename)

    @property
    def logfile(self):
        """Return path to logfile

        :returns: path to logfile within workflow's cache directory
        :rtype: `unicode`

        """

        return self.cachefile('%s.log' % self.bundleid)

    @property
    def logger(self):
        """Create and return a logger that logs to both console and
        a log file. Use `~Workflow.openlog` to open the log file in Console.

        :returns: an initialised logger
        :rtype: `~logging.Logger` instance

        """

        if not self._logger:
            # Initialise logging
            logfile = logging.handlers.RotatingFileHandler(self.logfile,
                                                           maxBytes=1024*1024,
                                                           backupCount=0)
            console = logging.StreamHandler()
            fmt = logging.Formatter('%(asctime)s %(filename)s:%(lineno)s'
                                    ' %(levelname)-8s %(message)s',
                                    datefmt='%H:%M:%S')
            logfile.setFormatter(fmt)
            console.setFormatter(fmt)
            logger = logging.getLogger('')
            logger.addHandler(logfile)
            logger.addHandler(console)
            logger.setLevel(logging.DEBUG)
            self._logger = logger

        return self._logger

    @logger.setter
    def logger(self, logger):
        """Set a custom logger.

        :param logger: The logger to use
        :type logger: `~logging.Logger` instance

        """

        self._logger = logger

    @property
    def settings_path(self):
        """Path to settings file within workflow's data directory

        :returns: path to ``settings.json`` file
        :rtype: `unicode`

        """

        if not self._settings_path:
            self._settings_path = self.datafile('settings.json')
        return self._settings_path

    @property
    def settings(self):
        """Return a dictionary subclass that saves itself when changed.

        :returns: `Settings` instance initialised with
                  `~Workflow._default_settings`
        :rtype: `Settings` instance

        """

        if not self._settings:
            self._settings = Settings(self.settings_path,
                                      self._default_settings)
        return self._settings

    def cached_data(self, name, data_func, max_age=60):
        """Retrieve data from cache or re-generate and re-cache data if
        stale/non-existant. If ``max_age`` is 0, return cached data no
        matter how old.

        :param name: name of datastore
        :type name: `unicode`
        :param data_func: function to (re-)generate data.
        :type data_func: `callable`
        :param max_age: maximum age of cached data in seconds
        :type max_age: `int`
        :returns: cached data or return value of ``data_func``
        :rtype: whatever ``data_func`` returns

        """

        cache_path = self.cachefile('%s.cache' % name)
        age = self.cached_data_age(name)
        if (age < max_age or max_age == 0) and os.path.exists(cache_path):
            with open(cache_path, 'rb') as file:
                self.logger.debug('Loading cached data from : %s',
                                  cache_path)
                return pickle.load(file)
        data = data_func()
        with open(cache_path, 'wb') as file:
            pickle.dump(data, file)
        self.logger.debug('Cached data saved at : %s', cache_path)
        return data

    def cached_data_fresh(self, name, max_age):
        """Is data cached at `name` less than `max_age` old?

        :param name: name of datastore
        :type name: `unicode`
        :param max_age: maximum age of data in seconds
        :type max_age: `int`
        :returns: True if data is less than `max_age` old
        :rtype: `Boolean`

        """

        return self.cached_data_age(name) < max_age

    def cached_data_age(self, name):
        """Return age of data cached at `name` in seconds or 0 if
        cache doesn't exist

        :param name: name of datastore
        :type name: `unicode`
        :returns: age of datastore in seconds
        :rtype: `int`

        """

        cache_path = self.cachefile('%s.cache' % name)
        if not os.path.exists(cache_path):
            return 0
        return time.time() - os.stat(cache_path).st_mtime

    def filter(self, query, items, key=lambda x: x, ascending=False,
               include_score=False):
        """Fuzzy search filter. Returns list of ``items`` that match ``query``.

        Matching is case-insensitive. Any item that does not contain the
        entirety of ``query`` is rejected.

        Results are matched as follows:

        1. Items whose capital letters match ``query``, e.g.
           ``of`` = ``OmniFocus``
        2. Items that start with ``query``. Shorter items are rated more highly
        3. Items whose "initials" match ``query``, e.g.
           ``goc`` = ``Game of Cards``
        4. Items that contain ``query`` as an "atom" (words between spaces
           and other non-letter characters).
        4. Items that contain all the characters in ``query``.
           Matches nearer the beginning of the item are prioritised,
           as are shorter items.

        :param query: query to test items against
        :type query: `unicode`
        :param items: iterable of items to test
        :type items: `iterable` (`list` or `tuple`)
        :param key: function to get comparison key from `items`. Must return a
                    `unicode` string.
        :type key: `callable`
        :param ascending: set to `True` to get worst matches first
        :type ascending: `Boolean`
        :param include_score: Useful for debugging the scoring algorithm.
            If `True`, results will be a list of tuples ``(item, score, rule)``.
        :type include_score: `Boolean`
        :returns: list of `items` matching ``query`` or list of
            ``(item, score, rule)`` `tuples` if `include_score` is `True`.
            ``rule`` is the name of the rule that matched the item.
        :rtype: `list`

        """

        results = {}
        query = query.lower()
        queryset = set(query)

        # Build pattern: include all characters
        pattern = []
        for c in query:
            # pattern.append('[^{0}]*{0}'.format(re.escape(c)))
            pattern.append('.*?{0}'.format(re.escape(c)))
        pattern = ''.join(pattern)
        search = re.compile(pattern, re.IGNORECASE).search
        # print('filter: searching %d items' % len(items))

        for item in items:
            rule = None
            score = 0
            value = key(item)

            # pre-filter any items that do not contain all characters of `query`
            # to save on running several more expensive tests
            if not queryset <= set(value.lower()):
                continue

            # item starts with query
            if value.lower().startswith(query):
                score = 100.0 - (len(value) - len(query))
                rule = 'startswith'

            else:
                # query matches capitalised letters in item,
                # e.g. of = OmniFocus
                initials = ''.join([c for c in value if c in INITIALS])
                if initials.lower().startswith(query):
                    score = 100.0 - (len(initials) - len(query))
                    rule = 'capitals'

                else:
                    # split the item into "atoms", i.e. words separated by
                    # spaces or other non-word characters
                    atoms = [s.lower() for s in split_on_delimiters(value)]
                    # print('atoms : %s  -->  %s' % (value, atoms))
                    # initials of the atoms
                    initials = ''.join([s[0] for s in atoms if s])

                    # is `query` one of the atoms in item?
                    # similar to substring, but scores more highly, as it's
                    # a word within the item
                    if query in atoms:
                        score = 100.0 - (len(value) - len(query))
                        rule = 'atom'

                    # `query` matches start (or all) of the initials of the
                    # atoms, e.g. ``himym`` matches "How I Met Your Mother"
                    # *and* "how i met your mother" (the ``capitals`` rule only
                    # matches the former)
                    elif initials.startswith(query):
                        score = 100.0 - (len(initials) - len(query))
                        rule = 'initials:startswith'

                    # `query` is a substring of initials, e.g. ``doh`` matches
                    # "The Dukes of Hazzard"
                    elif query in initials:
                        score = 95.0 - (len(initials) - len(query))
                        rule = 'initials:contains'

                    # `query` is a substring of item
                    elif query in value.lower():
                            score = 90.0 - (len(value) - len(query))
                            rule = 'substring'

                    # finally, assign a score based on how close together the
                    # characters in `query` are in item.
                    else:
                        match = search(value)
                        if match:
                            score = 100.0 / ((1 + match.start()) *
                                             (match.end() - match.start() + 1))
                            rule = 'allchars'

            if score > 0:
                # use "reversed" `score` (i.e. highest becomes lowest) and
                # `value` as sort key. This means items with the same score
                # will be sorted in alphabetical not reverse alphabetical order
                results[(100.0 / score, value.lower())] = (item, score, rule)

        # sort on keys, then discard the keys
        keys = sorted(results.keys(), reverse=ascending)
        results = [results.get(k) for k in keys]

        # return list of ``(item, score, rule)``
        if include_score:
            return results
        # just return list of items
        return [t[0] for t in results]

    def run(self, func):
        """Call `func` to run your workflow

        `func` will be called with `Workflow` instance as first argument.
        `func` should be the main entry point to your workflow.

        Any exceptions raised will be logged and an error message will be
        output to Alfred.

        :param func: Callable to call with `self` as first argument.

        """

        try:
            func(self)
        except Exception as err:
            self.logger.exception(err)
            if not sys.stdout.isatty():  # Show error in Alfred
                self._items = []
                if self._name:
                    name = self._name
                elif self._bundleid:
                    name = self._bundleid
                else:  # pragma: no cover
                    name = os.path.dirname(__file__)
                self.add_item("Error in workflow '%s'" % name, unicode(err),
                              icon=ICON_ERROR)
                self.send_feedback()
            return 1
        return 0

    # Alfred feedback methods ------------------------------------------

    def add_item(self, title, subtitle='', arg=None, autocomplete=None,
                 valid=False, uid=None, icon=None, icontype=None,
                 type=None):
        """Add an item to be output to Alfred

        :param title: Title shown in Alfred
        :type title: `unicode`
        :param subtitle: Subtitle shown in Alfred
        :type subtitle: `unicode`
        :param arg: Argument passed by Alfred as `{query}` when item is actioned
        :type arg: `unicode`
        :param autocomplete: Text expanded in Alfred when item is TABbed
        :type autocomplete: `unicode`
        :param valid: Whether or not item can be actioned
        :type valid: `Boolean`
        :uid: Used by Alfred to remember/sort items
        :type uid: `unicode`
        :icon: Filename of icon to use
        :type icon: `unicode`
        :param icontype: Type of icon. Must be one of `None` , ``filetype``
                   or ``fileicon``. Use ``filetype`` when ``icon`` is a
                   filetype such as ``public.folder``. Use ``fileicon``
                   when you wish to use the icon of the file specified
                   as ``icon``, e.g. ``icon='/Applications/Safari.app',
                   icontype='fileicon'``. Leave as `None` if ``icon`` points
                   to an actual icon file.
        :type icontype: `unicode`
        :param type: Result type. Currently only ``file`` is supported. This
                     will tell Alfred to enable file actions for this item.
        :type type: `unicode`
        :returns: `~workflow.Item` instance

        """

        item = self.item_class(title, subtitle, arg, autocomplete, valid,
                               uid, icon, icontype, type)
        self._items.append(item)
        return item

    def send_feedback(self):
        """Print stored items to console/Alfred as XML"""
        root = ET.Element('items')
        for item in self._items:
            root.append(item.elem)
        sys.stdout.write('<?xml version="1.0" encoding="utf-8"?>\n')
        sys.stdout.write(ET.tostring(root).encode('utf-8'))
        sys.stdout.flush()

    ####################################################################
    # Keychain password storage methods
    ####################################################################

    def save_password(self, account, password, service=None):
        """Save account credentials.

        If the account exists, the old password will first be deleted (Keychain
        throws an error otherwise).

        If something goes wrong, a `KeychainError` exception will be raised.

        :param account: name of the account the password is for, e.g. "Pinboard"
        :type account: `unicode`
        :param password: the password to secure
        :type password: `unicode`
        :param service: Name of the service. By default, this is the workflow's
                        bundle ID
        :type service: `unicode`

        """
        if not service:
            service = self.bundleid
        try:
            retcode, output = self._call_security('add-generic-password',
                                                  service, account,
                                                  '-w', password)
            self.logger.debug('Saved password : %s:%s', service, account)
        except PasswordExists:
            self.logger.debug('Password exists : %s:%s', service, account)
            current_password = self.get_password(account, service)
            if current_password == password:
                self.logger.debug('Password unchanged')
            else:
                self.delete_password(account, service)
                retcode, output = self._call_security('add-generic-password',
                                                      service, account,
                                                      '-w', password)
                self.logger.debug('save_password : %s:%s', service, account)

    def get_password(self, account, service=None):
        """Retrieve the password saved at `service/account`. Raise
        `PasswordNotFound` exception if password doesn't exist.

        :param account: name of the account the password is for, e.g. "Pinboard"
        :type account: `unicode`
        :param service: Name of the service. By default, this is the workflow's
                        bundle ID
        :type service: `unicode`
        :returns: account password
        :rtype: `unicode`

        """

        if not service:
            service = self.bundleid
        retcode, password = self._call_security('find-generic-password',
                                                service, account, '-w')
        self.logger.debug('get_password : %s:%s', service, account)
        return password

    def delete_password(self, account, service=None):
        """Delete the password stored at ``service/account``. Raises
        `PasswordNotFound` if account is unknown.

        :param account: name of the account the password is for, e.g. "Pinboard"
        :type account: `unicode`
        :param service: Name of the service. By default, this is the workflow's
                        bundle ID
        :type service: `unicode`

        """

        if not service:
            service = self.bundleid
        retcode, output = self._call_security('delete-generic-password',
                                              service, account)
        self.logger.debug('delete_password : %s:%s', service, account)

    ####################################################################
    # Methods for workflow:* magic args
    ####################################################################

    def openlog(self):
        """Open log file in standard application (usually Console.app)"""
        subprocess.call(['open', self.logfile])

    def clear_cache(self):
        """Delete all files in workflow cache directory"""
        if os.path.exists(self.cachedir):
            for filename in os.listdir(self.cachedir):
                path = os.path.join(self.cachedir, filename)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
                self.logger.debug('Deleted : %r', path)

    def clear_settings(self):
        """Delete settings file"""
        if os.path.exists(self.settings_path):
            os.unlink(self.settings_path)
            self.logger.debug('Deleted : %r', self.settings_path)

    ####################################################################
    # Helper methods
    ####################################################################

    def decode(self, text, encoding=None, normalization=None):
        """Return `text` as normalised unicode.

        If `encoding` and/or `normalization` is `None`, `self._input_encoding`
        and `self._normalizsation` will be used.

        :param text: string
        :type text: encoded string
        :param encoding:
        :type encoding: `unicode` or None
        :param normalization:
        :type normalization: `unicode` or None
        :returns: decoded and normalised `unicode`

        """

        encoding = encoding or self._input_encoding
        normalization = normalization or self._normalizsation
        return unicodedata.normalize(normalization, unicode(text, encoding))

    def _load_info_plist(self):
        """Load workflow info from ``info.plist``

        """

        self._info = plistlib.readPlist(self._info_plist)
        self._info_loaded = True

    def _create(self, dirpath):
        """Create directory `dirpath` if it doesn't exist

        :param dirpath: path to directory
        :type dirpath: `unicode`
        :returns: ``dirpath`` argument
        :rtype: `unicode`

        """

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        return dirpath

    def _call_security(self, action, service, account, *args):
        """Call the ``security`` CLI app that provides access to keychains.


        May raise `PasswordNotFound`, `PasswordExists` or `KeychainError`
        exceptions (the first two are subclasses of `KeychainError`).

        :param action: The ``security`` action to call, e.g.
                           ``add-generic-password``
        :type action: `unicode`
        :param service: Name of the service.
        :type service: `unicode`
        :param account: name of the account the password is for, e.g. "Pinboard"
        :type account: `unicode`
        :param password: the password to secure
        :type password: `unicode`
        :param *args: list of command line arguments to be passed to
                      ``security``
        :type *args: `list` or `tuple`
        :returns: ``(retcode, output)``. ``retcode`` is an `int`, ``output`` a
                  `unicode` string.
        :rtype: `tuple` (`int`, `unicode`)

        """

        cmd = ['security', action, '-s', service, '-a', account] + list(args)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retcode, output = p.wait(), p.stdout.read().strip().decode('utf-8')
        if retcode == 44:  # password does not exist
            raise PasswordNotFound()
        elif retcode == 45:  # password already exists
            raise PasswordExists()
        elif retcode > 0:
            err = KeychainError('Unknown Keychain error : %s' % output)
            err.retcode = retcode
            raise err
        return (retcode, output)
