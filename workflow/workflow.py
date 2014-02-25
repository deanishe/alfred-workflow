# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""
===========
workflow.py
===========

Helper for Alfred 2 workflows.

TODO: Add magic arguments for opening cache/data directories in Finder
"""

from __future__ import print_function, unicode_literals

import os
import sys
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
except ImportError:
    import xml.etree.ElementTree as ET


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
              '/Resources/GroupInfo.icns')
ICON_HELP = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/HelpInfo.icns')
ICON_NETWORK = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/GenericNetworkIcon.icns')
ICON_WEB = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
            '/Resources/BookmarkInfo.icns')
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


class Item(object):
    """A feedback item for Alfred.

    You probably shouldn't use this class directly, but via
    `Workflow.add_item`.

    """

    def __init__(self, title, subtitle='', arg=None, autocomplete=None,
                 valid=False, uid=None, icon=None, icontype=None,
                 type=None):
        """Arguments the same as for `Workflow.add_item`.

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

        :returns: `~xml.etree.ElementTree.Element` instance for `Item`

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

    """

    def __init__(self, filepath, **defaults):
        """Dictionary keys & values will be saved as a JSON file
        at `filepath`. If the file does not exist, the dictionary
        (and settings file) will be initialised with `defaults`.

        :param filepath: where to save the settings
        :type filepath: `unicode`
        :param **defaults: default settings

        """

        super(Settings, self).__init__()
        self._filepath = filepath
        self._nosave = False
        if not os.path.exists(self._filepath):
            for key, val in defaults.items():
                self[key] = val
            self._save()  # save default settings
        else:
            self._load()

    def _load(self):
        self._nosave = True
        with open(self._filepath, 'rb') as file:
            for key, value in json.load(file, encoding='utf-8').items():
                self[key] = value
        self._nosave = False

    def _save(self):
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
    """Helper class for Alfred workflow authors.

    """

    # Which class to use to generate feedback items. You probably
    # won't want to change this
    item_class = Item

    def __init__(self, default_settings=None, input_encoding='utf-8',
                 normalization='NFC', capture_args=True, libraries=None):
        """
        Create new Workflow instance.

        :param default_settings: default workflow settings
        :type default_settings: `dict`
        :param input_encoding: encoding of command line arguments
        :type input_encoding: `unicode`
        :param normalization: normalisation to apply to CLI args
        :type normalization: `unicode`. Use 'NFC'for Python, 'NFD' if working
                             with data from the filesystem.
        :param capture_args: capture and act on 'workflow:*' arguments
        :type capture_args: `Boolean`
        :param libraries: sequence of paths to directories containing
                          libraries. These paths will be added to `sys.path`.
        :type libraries: sequence (`tuple` or `list`)

        """

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
            for path in libraries:
                sys.path.insert(0, path)

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

        args = [self.decode(arg) for arg in sys.argv[1:]]
        if len(args) and self._capture_args:
            if 'workflow:openlog' in args:
                self.openlog()
                sys.exit(0)
            elif 'workflow:delcache' in args:
                self.clear_cache()
                sys.exit(0)
            elif 'workflow:delsettings' in args:
                self.clear_settings()
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
                                      **self._default_settings)
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
            self._items = []
            if self._name:
                name = self._name
            elif self._bundleid:
                name = self._bundleid
            else:
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
                               uid, icon)
        self._items.append(item)
        return item

    def send_feedback(self):
        """Print stored items to console/Alfred"""
        root = ET.Element('items')
        for item in self._items:
            root.append(item.elem)
        sys.stdout.write('<?xml version="1.0" encoding="utf-8"?>\n')
        sys.stdout.write(ET.tostring(root).encode('utf-8'))
        sys.stdout.flush()

    ####################################################################
    # Methods for workflow:* args
    ####################################################################

    def openlog(self):
        """Open log file"""
        subprocess.call(['open', self.logfile])

    def clear_cache(self):
        """Delete all files in workflow cache directory"""
        if os.path.exists(self.cachedir):
            for filename in os.listdir(self.cachedir):
                path = os.path.join(self.cachedir, filename)
                if os.path.isdir(path):
                    shutil.deltree(path)
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

        :returns: `None`

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
