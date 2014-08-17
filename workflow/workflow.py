# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""
Helper library for Alfred 2 workflow authors.

You probably only want to use the :class:`Workflow` class directly.

The :class:`Item` and :class:`Settings` classes are supporting classes,
which are meant to be accessed via :class:`Workflow` instances.

Classes :class:`SerializerManager`, :class:`JSONSerializer`,
:class:`CPickleSerializer` and :class:`PickleSerializer` are part of
the data/cache serialization features of :class:`Workflow`, accessible
by the module-level ``manager`` object.

To register a new serializer, do:

.. code-block:: python
   :linenos:

    from workflow import Workflow, manager


    class MySerializer(object):

        @classmethod
        def load(cls, file_obj):
            # load data from file_obj

        @classmethod
        def dump(cls, data, file_obj):
            # write data to file_obj

    manager.register('myformat', MySerializer())


The name under which you register your serializer will be used as the
file extension of any saved files.

To set the default serializer for cached data,
set :attr:`Workflow.cache_serializer`, and to set the default
serializer for stored data, set :attr:`Workflow.data_serializer`.

Cached data is stored in the Workflow's cache directory, which is intended
for temporary and easily regenerated data.

Stored data is stored in the Workflow's data directory, which is intended
for data that is user-generated or not easily recreated.

The default serializer for both cached and stored data is ``cpickle``.

For more information, please see :ref:`Persistent data <persistent-data>`.

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
import cPickle
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
ICON_ACCOUNT = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/Accounts.icns')
ICON_BURN = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/BurningIcon.icns')
ICON_COLOR = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/ProfileBackgroundColor.icns')
ICON_COLOUR = ICON_COLOR  # Queen's English, if you please
ICON_ERROR = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/AlertStopIcon.icns')
ICON_FAVORITE = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                 '/Resources/ToolbarFavoritesIcon.icns')
ICON_FAVOURITE = ICON_FAVORITE
ICON_GROUP = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/GroupIcon.icns')
ICON_HELP = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/HelpIcon.icns')
ICON_INFO = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/ToolbarInfo.icns')
ICON_MUSIC = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/ToolbarMusicFolderIcon.icns')
ICON_NETWORK = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/GenericNetworkIcon.icns')
ICON_NOTE = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/AlertNoteIcon.icns')
ICON_SETTINGS = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                 '/Resources/ToolbarAdvanced.icns')
ICON_SYNC = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/Sync.icns')
ICON_TRASH = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/TrashIcon.icns')
ICON_USER = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
             '/Resources/UserIcon.icns')
ICON_WARNING = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/AlertCautionIcon.icns')
ICON_WEB = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
            '/Resources/BookmarkIcon.icns')

####################################################################
# non-ASCII to ASCII diacritic folding.
# Used by ``fold_to_ascii`` method
####################################################################

ASCII_REPLACEMENTS = {
    'À': 'A',
    'Á': 'A',
    'Â': 'A',
    'Ã': 'A',
    'Ä': 'A',
    'Å': 'A',
    'Æ': 'AE',
    'Ç': 'C',
    'È': 'E',
    'É': 'E',
    'Ê': 'E',
    'Ë': 'E',
    'Ì': 'I',
    'Í': 'I',
    'Î': 'I',
    'Ï': 'I',
    'Ð': 'D',
    'Ñ': 'N',
    'Ò': 'O',
    'Ó': 'O',
    'Ô': 'O',
    'Õ': 'O',
    'Ö': 'O',
    'Ø': 'O',
    'Ù': 'U',
    'Ú': 'U',
    'Û': 'U',
    'Ü': 'U',
    'Ý': 'Y',
    'Þ': 'Th',
    'ß': 'ss',
    'à': 'a',
    'á': 'a',
    'â': 'a',
    'ã': 'a',
    'ä': 'a',
    'å': 'a',
    'æ': 'ae',
    'ç': 'c',
    'è': 'e',
    'é': 'e',
    'ê': 'e',
    'ë': 'e',
    'ì': 'i',
    'í': 'i',
    'î': 'i',
    'ï': 'i',
    'ð': 'd',
    'ñ': 'n',
    'ò': 'o',
    'ó': 'o',
    'ô': 'o',
    'õ': 'o',
    'ö': 'o',
    'ø': 'o',
    'ù': 'u',
    'ú': 'u',
    'û': 'u',
    'ü': 'u',
    'ý': 'y',
    'þ': 'th',
    'ÿ': 'y',
    'Ł': 'L',
    'ł': 'l',
    'Ń': 'N',
    'ń': 'n',
    'Ņ': 'N',
    'ņ': 'n',
    'Ň': 'N',
    'ň': 'n',
    'Ŋ': 'ng',
    'ŋ': 'NG',
    'Ō': 'O',
    'ō': 'o',
    'Ŏ': 'O',
    'ŏ': 'o',
    'Ő': 'O',
    'ő': 'o',
    'Œ': 'OE',
    'œ': 'oe',
    'Ŕ': 'R',
    'ŕ': 'r',
    'Ŗ': 'R',
    'ŗ': 'r',
    'Ř': 'R',
    'ř': 'r',
    'Ś': 'S',
    'ś': 's',
    'Ŝ': 'S',
    'ŝ': 's',
    'Ş': 'S',
    'ş': 's',
    'Š': 'S',
    'š': 's',
    'Ţ': 'T',
    'ţ': 't',
    'Ť': 'T',
    'ť': 't',
    'Ŧ': 'T',
    'ŧ': 't',
    'Ũ': 'U',
    'ũ': 'u',
    'Ū': 'U',
    'ū': 'u',
    'Ŭ': 'U',
    'ŭ': 'u',
    'Ů': 'U',
    'ů': 'u',
    'Ű': 'U',
    'ű': 'u',
    'Ŵ': 'W',
    'ŵ': 'w',
    'Ŷ': 'Y',
    'ŷ': 'y',
    'Ÿ': 'Y',
    'Ź': 'Z',
    'ź': 'z',
    'Ż': 'Z',
    'ż': 'z',
    'Ž': 'Z',
    'ž': 'z',
    'ſ': 's',
    'Α': 'A',
    'Β': 'B',
    'Γ': 'G',
    'Δ': 'D',
    'Ε': 'E',
    'Ζ': 'Z',
    'Η': 'E',
    'Θ': 'Th',
    'Ι': 'I',
    'Κ': 'K',
    'Λ': 'L',
    'Μ': 'M',
    'Ν': 'N',
    'Ξ': 'Ks',
    'Ο': 'O',
    'Π': 'P',
    'Ρ': 'R',
    'Σ': 'S',
    'Τ': 'T',
    'Υ': 'U',
    'Φ': 'Ph',
    'Χ': 'Kh',
    'Ψ': 'Ps',
    'Ω': 'O',
    'α': 'a',
    'β': 'b',
    'γ': 'g',
    'δ': 'd',
    'ε': 'e',
    'ζ': 'z',
    'η': 'e',
    'θ': 'th',
    'ι': 'i',
    'κ': 'k',
    'λ': 'l',
    'μ': 'm',
    'ν': 'n',
    'ξ': 'x',
    'ο': 'o',
    'π': 'p',
    'ρ': 'r',
    'ς': 's',
    'σ': 's',
    'τ': 't',
    'υ': 'u',
    'φ': 'ph',
    'χ': 'kh',
    'ψ': 'ps',
    'ω': 'o',
    'А': 'A',
    'Б': 'B',
    'В': 'V',
    'Г': 'G',
    'Д': 'D',
    'Е': 'E',
    'Ж': 'Zh',
    'З': 'Z',
    'И': 'I',
    'Й': 'I',
    'К': 'K',
    'Л': 'L',
    'М': 'M',
    'Н': 'N',
    'О': 'O',
    'П': 'P',
    'Р': 'R',
    'С': 'S',
    'Т': 'T',
    'У': 'U',
    'Ф': 'F',
    'Х': 'Kh',
    'Ц': 'Ts',
    'Ч': 'Ch',
    'Ш': 'Sh',
    'Щ': 'Shch',
    'Ъ': "'",
    'Ы': 'Y',
    'Ь': "'",
    'Э': 'E',
    'Ю': 'Iu',
    'Я': 'Ia',
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'i',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': "'",
    'ы': 'y',
    'ь': "'",
    'э': 'e',
    'ю': 'iu',
    'я': 'ia',
    # 'ᴀ': '',
    # 'ᴁ': '',
    # 'ᴂ': '',
    # 'ᴃ': '',
    # 'ᴄ': '',
    # 'ᴅ': '',
    # 'ᴆ': '',
    # 'ᴇ': '',
    # 'ᴈ': '',
    # 'ᴉ': '',
    # 'ᴊ': '',
    # 'ᴋ': '',
    # 'ᴌ': '',
    # 'ᴍ': '',
    # 'ᴎ': '',
    # 'ᴏ': '',
    # 'ᴐ': '',
    # 'ᴑ': '',
    # 'ᴒ': '',
    # 'ᴓ': '',
    # 'ᴔ': '',
    # 'ᴕ': '',
    # 'ᴖ': '',
    # 'ᴗ': '',
    # 'ᴘ': '',
    # 'ᴙ': '',
    # 'ᴚ': '',
    # 'ᴛ': '',
    # 'ᴜ': '',
    # 'ᴝ': '',
    # 'ᴞ': '',
    # 'ᴟ': '',
    # 'ᴠ': '',
    # 'ᴡ': '',
    # 'ᴢ': '',
    # 'ᴣ': '',
    # 'ᴤ': '',
    # 'ᴥ': '',
    'ᴦ': 'G',
    'ᴧ': 'L',
    'ᴨ': 'P',
    'ᴩ': 'R',
    'ᴪ': 'PS',
    'ẞ': 'Ss',
    'Ỳ': 'Y',
    'ỳ': 'y',
    'Ỵ': 'Y',
    'ỵ': 'y',
    'Ỹ': 'Y',
    'ỹ': 'y',
}

####################################################################
# Used by `Workflow.filter`
####################################################################

# Anchor characters in a name
INITIALS = string.ascii_uppercase + string.digits

# Split on non-letters, numbers
split_on_delimiters = re.compile('[^a-zA-Z0-9]').split

# Match filter flags
MATCH_STARTSWITH = 1
MATCH_CAPITALS = 2
MATCH_ATOM = 4
MATCH_INITIALS_STARTSWITH = 8
MATCH_INITIALS_CONTAIN = 16
MATCH_INITIALS = 24
MATCH_SUBSTRING = 32
MATCH_ALLCHARS = 64
MATCH_ALL = 127


####################################################################
# Keychain access errors
####################################################################

class KeychainError(Exception):
    """Raised by methods :meth:`Workflow.save_password`,
    :meth:`Workflow.get_password` and :meth:`Workflow.delete_password`
    when ``security`` CLI app returns an unknown code.

    """


class PasswordNotFound(KeychainError):
    """Raised by method :meth:`Workflow.get_password` when ``account``
    is unknown to the Keychain.

    """


class PasswordExists(KeychainError):
    """Raised when trying to overwrite an existing account password.

    The API user should never receive this error: it is used internally
    by the :meth:`Workflow.save_password` method.

    """


####################################################################
# Helper functions
####################################################################

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


####################################################################
# Implementation classes
####################################################################

class SerializerManager(object):
    """Contains registered serializers.

    .. versionadded:: 1.8

    A configured instance of this class is available at ``workflow.manager``.

    Use :meth:`register()` to register new (or replace
    existing) serializers, which you can specify by name when calling
    :class:`Workflow` data storage methods.

    A ``serializer`` object must have ``load()`` and ``dump()`` methods
    that work the same way as in the built-in :mod:`json` and
    :mod:`pickle` libraries, i.e.:

    .. code-block:: python
        :linenos:

        # Reading
        data = serializer.load(open('filename', 'rb'))
        # Writing
        serializer.dump(data, open('filename', 'wb'))

    There are 3 pre-configured serializers: ``json``, ``pickle``
    and ``cpickle``. The default is ``cpickle``, as it is very fast and
    can handle most Python objects.

    If you need custom pickling, use the ``pickle`` serializer instead.

    Be careful using ``json``: JSON only supports a subset of Python's
    native data types (e.g., no ``tuple`` or :class:`set`) and
    doesn't, for example, support ``dict`` keys that aren't strings.

    See the built-in :mod:`cPickle`, :mod:`pickle` and :mod:`json`
    libraries for more information on the serialization formats.

    """

    def __init__(self):
        self._serializers = {}

    def register(self, name, serializer):
        """Register ``serializer`` object under ``name``.

        Raises :class:`AttributeError` if ``serializer`` in invalid.

        **Note:** ``name`` will be used as the file extension of the
        saved files.

        :param name: Name to register ``serializer`` under
        :type name: ``unicode`` or ``str``
        :param serializer: object with ``load()`` and ``dump()``
            methods

        """

        # Basic validation
        getattr(serializer, 'load')
        getattr(serializer, 'dump')

        self._serializers[name] = serializer

    def serializer(self, name):
        """Return serializer object for ``name`` or ``None`` if no such
        serializer is registered

        :param name: Name of serializer to return
        :type name: ``unicode`` or ``str``
        :returns: serializer object or ``None``

        """

        return self._serializers.get(name)

    def unregister(self, name):
        """Remove registered serializer with ``name``

        Raises a :class:`ValueError` if there is no such registered
        serializer.

        :param name: Name of serializer to remove
        :type name: ``unicode`` or ``str``
        :returns: serializer object

        """

        if name not in self._serializers:
            raise ValueError('No such serializer registered : {}'.format(name))

        serializer = self._serializers[name]
        del self._serializers[name]

        return serializer

    @property
    def serializers(self):
        """Return names of registered serializers"""
        return sorted(self._serializers.keys())


class JSONSerializer(object):
    """Wrapper around :mod:`json`. Sets ``indent`` and ``encoding``.

    .. versionadded:: 1.8

    Use this serializer if you need readable data files. JSON doesn't
    support Python objects as well as ``cPickle``/``pickle``, so be
    careful which data you try to serialize as JSON.

    """

    @classmethod
    def load(cls, file_obj):
        return json.load(file_obj)

    @classmethod
    def dump(cls, obj, file_obj):
        return json.dump(obj, file_obj, indent=2, encoding='utf-8')


class CPickleSerializer(object):
    """Wrapper around :mod:`cPickle`. Sets ``protocol``.

    .. versionadded:: 1.8

    This is the default serializer and the best combination of speed and
    flexibility.

    """

    @classmethod
    def load(cls, file_obj):
        return cPickle.load(file_obj)

    @classmethod
    def dump(cls, obj, file_obj):
        return cPickle.dump(obj, file_obj, protocol=-1)


class PickleSerializer(object):
    """Wrapper around :mod:`pickle`. Sets ``protocol``.

    .. versionadded:: 1.8

    Use this serializer if you need to add custom pickling.

    """

    @classmethod
    def load(cls, file_obj):
        return pickle.load(file_obj)

    @classmethod
    def dump(cls, obj, file_obj):
        return pickle.dump(obj, file_obj, protocol=-1)


# Set up default manager and register built-in serializers
manager = SerializerManager()
manager.register('cpickle', CPickleSerializer)
manager.register('pickle', PickleSerializer)
manager.register('json', JSONSerializer)


class Item(object):
    """Represents a feedback item for Alfred. Generates Alfred-compliant
    XML for a single item.

    You probably shouldn't use this class directly, but via
    :meth:`Workflow.add_item`. See :meth:`~Workflow.add_item`
    for details of arguments.

    """

    def __init__(self, title, subtitle='', modifier_subtitles=None,
                 arg=None, autocomplete=None, valid=False, uid=None,
                 icon=None, icontype=None, type=None):
        """Arguments the same as for :meth:`Workflow.add_item`.

        """

        self.title = title
        self.subtitle = subtitle
        self.modifier_subtitles = modifier_subtitles or {}
        self.arg = arg
        self.autocomplete = autocomplete
        self.valid = valid
        self.uid = uid
        self.icon = icon
        self.icontype = icontype
        self.type = type

    @property
    def elem(self):
        """Create and return feedback item for Alfred.

        :returns: :class:`ElementTree.Element <xml.etree.ElementTree.Element>`
            instance for this :class:`Item` instance.

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
        # Add modifier subtitles
        for mod in ('cmd', 'ctrl', 'alt', 'shift', 'fn'):
            if mod in self.modifier_subtitles:
                ET.SubElement(root, 'subtitle',
                              {'mod': mod}).text = self.modifier_subtitles[mod]

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

    Dictionary keys & values will be saved as a JSON file
    at ``filepath``. If the file does not exist, the dictionary
    (and settings file) will be initialised with ``defaults``.

    :param filepath: where to save the settings
    :type filepath: :class:`unicode`
    :param defaults: dict of default settings
    :type defaults: :class:`dict`


    An appropriate instance is provided by :class:`Workflow` instances at
    :attr:`Workflow.settings`.

    """

    def __init__(self, filepath, defaults=None):

        super(Settings, self).__init__()
        self._filepath = filepath
        self._nosave = False
        if os.path.exists(self._filepath):
            self._load()
        elif defaults:
            for key, val in defaults.items():
                self[key] = val
            self.save()  # save default settings

    def _load(self):
        """Load cached settings from JSON file `self._filepath`"""

        self._nosave = True
        with open(self._filepath, 'rb') as file:
            for key, value in json.load(file, encoding='utf-8').items():
                self[key] = value
        self._nosave = False

    def save(self):
        """Save settings to JSON file specified in ``self._filepath``

        If you're using this class via :attr:`Workflow.settings`, which
        you probably are, ``self._filepath`` will be ``settings.json``
        in your workflow's data directory (see :attr:`~Workflow.datadir`).
        """
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
        self.save()

    def update(self, *args, **kwargs):
        """Override :class:`dict` method to save on update."""
        super(Settings, self).update(*args, **kwargs)
        self.save()

    def setdefault(self, key, value=None):
        """Override :class:`dict` method to save on update."""
        ret = super(Settings, self).setdefault(key, value)
        self.save()
        return ret


class Workflow(object):
    """Create new :class:`Workflow` instance.

        :param default_settings: default workflow settings. If no settings file
            exists, :class:`Workflow.settings` will be pre-populated with
            ``default_settings``.
        :type default_settings: :class:`dict`
        :param input_encoding: encoding of command line arguments
        :type input_encoding: :class:`unicode`
        :param normalization: normalisation to apply to CLI args.
            See :meth:`Workflow.decode` for more details.
        :type normalization: :class:`unicode`
        :param capture_args: capture and act on ``workflow:*`` arguments. See
            :ref:`Magic arguments <magic-arguments>` for details.
        :type capture_args: :class:`Boolean`
        :param libraries: sequence of paths to directories containing
            libraries. These paths will be prepended to ``sys.path``.
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
        self._workflowdir = None
        self._settings_path = None
        self._settings = None
        self._bundleid = None
        self._name = None
        self._cache_serializer = 'cpickle'
        self._data_serializer = 'cpickle'
        # info.plist should be in the directory above this one
        self._info_plist = self.workflowfile('info.plist')
        self._info = None
        self._info_loaded = False
        self._logger = None
        self._items = []
        self._alfred_env = None
        self._search_pattern_cache = {}
        if libraries:
            sys.path = libraries + sys.path

    ####################################################################
    # API methods
    ####################################################################

    # info.plist contents and alfred_* environment variables  ----------

    @property
    def alfred_env(self):
        """Alfred's environmental variables minus the ``alfred_`` prefix.

        .. versionadded:: 1.7

        The variables Alfred 2.4+ exports are:

        ============================  =========================================
        Variable                      Description
        ============================  =========================================
        alfred_preferences            Path to Alfred.alfredpreferences
                                      (where your workflows and settings are
                                      stored).
        alfred_preferences_localhash  Machine-specific preferences are stored
                                      in ``Alfred.alfredpreferences/preferences/local/<hash>``
                                      (see ``alfred_preferences`` above for
                                      the path to ``Alfred.alfredpreferences``)
        alfred_theme                  ID of selected theme
        alfred_theme_background       Background colour of selected theme in
                                      format ``rgba(r,g,b,a)``
        alfred_theme_subtext          Show result subtext.
                                      ``0`` = Always,
                                      ``1`` = Alternative actions only,
                                      ``2`` = Selected result only,
                                      ``3`` = Never
        alfred_version                Alfred version number, e.g. ``2.4``
        alfred_version_build          Alfred build number, e.g. ``277``
        alfred_workflow_bundleid      Bundle ID, e.g.
                                      ``net.deanishe.alfred-mailto``
        alfred_workflow_cache         Path to workflow's cache directory
        alfred_workflow_data          Path to workflow's data directory
        alfred_workflow_name          Name of current workflow
        alfred_workflow_uid           UID of workflow
        ============================  =========================================

        **Note:** all values are Unicode strings

        :returns: ``dict`` of Alfred's environmental variables without the
            ``alfred_`` prefix, e.g. ``preferences``, ``workflow_data``.

        """

        if self._alfred_env is not None:
            return self._alfred_env

        data = {}

        for key in (
                'alfred_preferences',
                'alfred_preferences_localhash',
                'alfred_theme',
                'alfred_theme_background',
                'alfred_theme_subtext',
                'alfred_version',
                'alfred_version_build',
                'alfred_workflow_bundleid',
                'alfred_workflow_cache',
                'alfred_workflow_data',
                'alfred_workflow_name',
                'alfred_workflow_uid'):

            value = os.getenv(key)

            if isinstance(value, str):
                value = self.decode(value)

            data[key[7:]] = value

        self._alfred_env = data

        return self._alfred_env

    @property
    def info(self):
        """`dict` of ``info.plist`` contents.

        :returns: ``dict``

        """

        if not self._info_loaded:
            self._load_info_plist()
        return self._info

    @property
    def bundleid(self):
        """Workflow bundle ID from ``info.plist``.

        :returns: bundle ID
        :rtype: ``unicode``

        """

        if not self._bundleid:
            if self.alfred_env.get('workflow_bundleid'):
                self._bundleid = self.alfred_env.get('workflow_bundleid')
            else:
                self._bundleid = unicode(self.info['bundleid'], 'utf-8')

        return self._bundleid

    @property
    def name(self):
        """Workflow name from ``info.plist``.

        :returns: workflow name
        :rtype: ``unicode``

        """

        if not self._name:
            if self.alfred_env.get('workflow_name'):
                self._name = self.alfred_env.get('workflow_name')
            else:
                self._name = unicode(self.info['name'], 'utf-8')

        return self._name

    # Workflow utility methods -----------------------------------------

    @property
    def args(self):
        """Return command line args as normalised unicode.

        Args are decoded and normalised via :meth:`~Workflow.decode`.

        The encoding and normalisation are the ``input_encoding`` and
        ``normalization`` arguments passed to :class:`Workflow` (``UTF-8``
        and ``NFC`` are the defaults).

        If :class:`Workflow` is called with ``capture_args=True`` (the default),
        :class:`Workflow` will look for certain ``workflow:*`` args and, if
        found, perform the corresponding actions and exit the workflow.

        See :ref:`Magic arguments <magic-arguments>` for details.

        """

        msg = None
        args = [self.decode(arg) for arg in sys.argv[1:]]
        if len(args) and self._capture_args:  # pragma: no cover
            if 'workflow:openlog' in args:
                msg = 'Opening workflow log file'
                self.open_log()
            elif 'workflow:reset' in args:
                self.reset()
                msg = 'Reset workflow'
            elif 'workflow:delcache' in args:
                self.clear_cache()
                msg = 'Deleted workflow cache'
            elif 'workflow:deldata' in args:
                self.clear_data()
                msg = 'Deleted workflow data'
            elif 'workflow:delsettings' in args:
                self.clear_settings()
                msg = 'Deleted workflow settings'
            elif 'workflow:openworkflow' in args:
                msg = 'Opening workflow directory'
                self.open_workflowdir()
            elif 'workflow:opendata' in args:
                msg = 'Opening workflow data directory'
                self.open_datadir()
            elif 'workflow:opencache' in args:
                msg = 'Opening workflow cache directory'
                self.open_cachedir()
            elif 'workflow:openterm' in args:
                msg = 'Opening workflow root directory in Terminal'
                self.open_terminal()
            elif 'workflow:foldingon' in args:
                msg = 'Diacritics will always be folded'
                self.settings['__workflows_diacritic_folding'] = True
            elif 'workflow:foldingoff' in args:
                msg = 'Diacritics will never be folded'
                self.settings['__workflows_diacritic_folding'] = False
            elif 'workflow:foldingdefault' in args:
                msg = 'Diacritics folding reset'
                if '__workflows_diacritic_folding' in self.settings:
                    del self.settings['__workflows_diacritic_folding']

            if msg:
                self.logger.debug(msg)
                if not sys.stdout.isatty():  # Show message in Alfred
                    self.add_item(msg, valid=False, icon=ICON_INFO)
                    self.send_feedback()
                sys.exit(0)
        return args

    @property
    def cachedir(self):
        """Path to workflow's cache directory.

        The cache directory is a subdirectory of Alfred's own cache directory in
        ``~/Library/Caches``. The full path is:

        ``~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/<bundle id>``

        :returns: full path to workflow's cache directory
        :rtype: ``unicode``

        """

        if self.alfred_env.get('workflow_cache'):
            dirpath = self.alfred_env.get('workflow_cache')
        else:
            dirpath = os.path.join(
                os.path.expanduser(
                    '~/Library/Caches/com.runningwithcrayons.Alfred-2/'
                    'Workflow Data/'),
                self.bundleid)

        return self._create(dirpath)

    @property
    def datadir(self):
        """Path to workflow's data directory.

        The data directory is a subdirectory of Alfred's own data directory in
        ``~/Library/Application Support``. The full path is:

        ``~/Library/Application Support/Alfred 2/Workflow Data/<bundle id>``

        :returns: full path to workflow data directory
        :rtype: ``unicode``

        """

        if self.alfred_env.get('workflow_data'):
            dirpath = self.alfred_env.get('workflow_data')
        else:
            dirpath = os.path.join(os.path.expanduser(
                '~/Library/Application Support/Alfred 2/Workflow Data/'),
                self.bundleid)

        return self._create(dirpath)

    @property
    def workflowdir(self):
        """Path to workflow's root directory (where ``info.plist`` is).

        :returns: full path to workflow root directory
        :rtype: ``unicode``

        """

        if not self._workflowdir:
            # Try the working directory first, then the directory
            # the library is in. CWD will be the workflow root if
            # a workflow is being run in Alfred
            candidates = [
                os.path.abspath(os.getcwd()),
                os.path.dirname(os.path.abspath(os.path.dirname(__file__)))]

            # climb the directory tree until we find `info.plist`
            for dirpath in candidates:

                while True:
                    if os.path.exists(os.path.join(dirpath, 'info.plist')):
                        self._workflowdir = dirpath
                        break
                    elif dirpath == '/':
                        # no `info.plist` found
                        break
                    dirpath = os.path.dirname(dirpath)

                # No need to check other candidates
                if self._workflowdir:
                    break

            if not self._workflowdir:
                raise IOError("'info.plist' not found in directory tree")

        return self._workflowdir

    def cachefile(self, filename):
        """Return full path to ``filename`` within your workflow's
        :attr:`cache directory <Workflow.cachedir>`.

        :param filename: basename of file
        :type filename: ``unicode``
        :returns: full path to file within cache directory
        :rtype: ``unicode``

        """

        return os.path.join(self.cachedir, filename)

    def datafile(self, filename):
        """Return full path to ``filename`` within your workflow's
        :attr:`data directory <Workflow.datadir>`.

        :param filename: basename of file
        :type filename: ``unicode``
        :returns: full path to file within data directory
        :rtype: ``unicode``

        """

        return os.path.join(self.datadir, filename)

    def workflowfile(self, filename):
        """Return full path to ``filename`` in workflow's root dir
        (where ``info.plist`` is).

        :param filename: basename of file
        :type filename: ``unicode``
        :returns: full path to file within data directory
        :rtype: ``unicode``

        """

        return os.path.join(self.workflowdir, filename)

    @property
    def logfile(self):
        """Return path to logfile

        :returns: path to logfile within workflow's cache directory
        :rtype: ``unicode``

        """

        return self.cachefile('%s.log' % self.bundleid)

    @property
    def logger(self):
        """Create and return a logger that logs to both console and
        a log file. Use `~Workflow.openlog` to open the log file in Console.

        :returns: an initialised logger
        :rtype: `~logging.Logger` instance

        """

        if self._logger:
            return self._logger

        # Initialise new logger and optionally handlers
        logger = logging.getLogger('workflow')

        if not logger.handlers:  # Only add one set of handlers
            logfile = logging.handlers.RotatingFileHandler(
                self.logfile,
                maxBytes=1024*1024,
                backupCount=0)

            console = logging.StreamHandler()

            fmt = logging.Formatter(
                '%(asctime)s %(filename)s:%(lineno)s'
                ' %(levelname)-8s %(message)s',
                datefmt='%H:%M:%S')

            logfile.setFormatter(fmt)
            console.setFormatter(fmt)

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
        """Path to settings file within workflow's data directory.

        :returns: path to ``settings.json`` file
        :rtype: ``unicode``

        """

        if not self._settings_path:
            self._settings_path = self.datafile('settings.json')
        return self._settings_path

    @property
    def settings(self):
        """Return a dictionary subclass that saves itself when changed.

        :returns: :class:`Settings` instance initialised from the data
            in JSON file at :attr:`settings_path` or if that doesn't exist,
            with the ``default_settings`` ``dict`` passed to :class:`Workflow`.
        :rtype: :class:`Settings` instance

        """

        if not self._settings:
            self._settings = Settings(self.settings_path,
                                      self._default_settings)
        return self._settings

    @property
    def cache_serializer(self):
        """Name of default cache serializer.

        .. versionadded:: 1.8

        This serializer is used by :meth:`cache_data()` and
        :meth:`cached_data()`

        See :class:`SerializerManager` for details.

        :returns: serializer name
        :rtype: ``unicode``

        """

        return self._cache_serializer

    @cache_serializer.setter
    def cache_serializer(self, serializer_name):
        """Set the default cache serialization format.

        .. versionadded:: 1.8

        This serializer is used by :meth:`cache_data()` and
        :meth:`cached_data()`

        The specified serializer must already by registered with the
        :class:`SerializerManager` at `~workflow.workflow.manager`,
        otherwise a :class:`ValueError` will be raised.

        :param serializer_name: Name of default serializer to use.
        :type serializer_name:

        """

        if manager.serializer(serializer_name) is None:
            raise ValueError(
                'Unknown serializer : `{}`. Register your serializer '
                'with `manager` first.'.format(serializer_name))

        self.logger.debug(
            'default cache serializer set to `{}`'.format(serializer_name))

        self._cache_serializer = serializer_name

    @property
    def data_serializer(self):
        """Name of default data serializer.

        .. versionadded:: 1.8

        This serializer is used by :meth:`store_data()` and
        :meth:`stored_data()`

        See :class:`SerializerManager` for details.

        :returns: serializer name
        :rtype: ``unicode``

        """

        return self._data_serializer

    @data_serializer.setter
    def data_serializer(self, serializer_name):
        """Set the default cache serialization format.

        .. versionadded:: 1.8

        This serializer is used by :meth:`store_data()` and
        :meth:`stored_data()`

        The specified serializer must already by registered with the
        :class:`SerializerManager` at `~workflow.workflow.manager`,
        otherwise a :class:`ValueError` will be raised.

        :param serializer_name: Name of default serializer to use.
        :type serializer_name:

        """

        if manager.serializer(serializer_name) is None:
            raise ValueError(
                'Unknown serializer : `{}`. Register your serializer '
                'with `manager` first.'.format(serializer_name))

        self.logger.debug(
            'default data serializer set to `{}`'.format(serializer_name))

        self._data_serializer = serializer_name

    def stored_data(self, name):
        """Retrieve data from data directory. Returns ``None`` if there
        is no data stored.

        .. versionadded:: 1.8

        :param name: name of datastore
        :type name: ``unicode``

        """

        metadata_path = self.datafile('.{}.alfred-workflow'.format(name))

        if not os.path.exists(metadata_path):
            self.logger.debug('No data stored for `{}`'.format(name))
            return None

        with open(metadata_path, 'rb') as file_obj:
            serializer_name = file_obj.read().strip()

        serializer = manager.serializer(serializer_name)

        if serializer is None:
            raise ValueError(
                'Unknown serializer `{}`. Register a corresponding serializer '
                'with `manager.register()` to load this data.'.format(
                serializer_name))

        self.logger.debug('Data `{}` stored in `{}` format'.format(
                          name, serializer_name))

        filename = '{}.{}'.format(name, serializer_name)
        data_path = self.datafile(filename)

        if not os.path.exists(data_path):
            self.logger.debug('No data stored for `{}`'.format(name))
            if os.path.exists(metadata_path):
                os.unlink(metadata_path)

            return None

        with open(data_path, 'rb') as file_obj:
            data = serializer.load(file_obj)

        self.logger.debug('Stored data loaded from : {}'.format(data_path))

        return data

    def store_data(self, name, data, serializer=None):
        """Save data to data directory.

        .. versionadded:: 1.8

        If ``data`` is ``None``, the datastore will be deleted.

        :param name: name of datastore
        :type name: ``unicode``
        :param data: object(s) to store
        :type data: artibrary Python objects. **Note:** some serializers
            can only handled certain types of data.
        :param serializer: name of serializer to use.
            See :class:`SerializerManager` for more information.
        :type serializer: ``unicode``
        :returns: data in datastore or ``None``

        """

        serializer_name = serializer or self.data_serializer

        if serializer_name == 'json' and name == 'settings':
            raise ValueError(
                'Cannot save data to `settings` with format `json`. '
                "This would overwrite Alfred-Workflow's settings file.")

        serializer = manager.serializer(serializer_name)

        if serializer is None:
            raise ValueError(
                'Invalid serializer `{}`. Register your serializer with '
                '`manager.register()` first.'.format(serializer_name))

        # In order for `stored_data()` to be able to load data stored with
        # an arbitrary serializer, yet still have meaningful file extensions,
        # the format (i.e. extension) is saved to an accompanying file
        metadata_path = self.datafile('.{}.alfred-workflow'.format(name))
        filename = '{}.{}'.format(name, serializer_name)
        data_path = self.datafile(filename)

        if data is None:  # Delete cached data
            for path in (metadata_path, data_path):
                if os.path.exists(path):
                    os.unlink(path)
                    self.logger.debug('Deleted data file : {}'.format(path))

            return

        # Save file extension
        with open(metadata_path, 'wb') as file_obj:
            file_obj.write(serializer_name)

        with open(data_path, 'wb') as file_obj:
            serializer.dump(data, file_obj)

        self.logger.debug('Stored data saved at : {}'.format(data_path))

    def cached_data(self, name, data_func=None, max_age=60):
        """Retrieve data from cache or re-generate and re-cache data if
        stale/non-existant. If ``max_age`` is 0, return cached data no
        matter how old.

        :param name: name of datastore
        :type name: ``unicode``
        :param data_func: function to (re-)generate data.
        :type data_func: `callable`
        :param max_age: maximum age of cached data in seconds
        :type max_age: `int`
        :returns: cached data, return value of ``data_func`` or ``None``
            if ``data_func`` is not set
        :rtype: whatever ``data_func`` returns or ``None``

        """

        serializer = manager.serializer(self.cache_serializer)

        cache_path = self.cachefile('%s.%s' % (name, self.cache_serializer))
        age = self.cached_data_age(name)

        if (age < max_age or max_age == 0) and os.path.exists(cache_path):

            with open(cache_path, 'rb') as file:
                self.logger.debug('Loading cached data from : %s',
                                  cache_path)
                return serializer.load(file)

        if not data_func:
            return None

        data = data_func()
        self.cache_data(name, data)

        return data

    def cache_data(self, name, data):
        """Save ``data`` to cache under ``name``.

        If ``data`` is ``None``, the corresponding cache file will be deleted.

        :param name: name of datastore
        :type name: ``unicode``
        :param data: data to store
        :type data: any object supported by :mod:`pickle`

        """

        serializer = manager.serializer(self.cache_serializer)

        cache_path = self.cachefile('%s.%s' % (name, self.cache_serializer))

        if data is None:
            if os.path.exists(cache_path):
                os.unlink(cache_path)
                self.logger.debug('Deleted cache file : %s', cache_path)
            return

        with open(cache_path, 'wb') as file:
            serializer.dump(data, file)

        self.logger.debug('Cached data saved at : %s', cache_path)

    def cached_data_fresh(self, name, max_age):
        """Is data cached at `name` less than `max_age` old?

        :param name: name of datastore
        :type name: ``unicode``
        :param max_age: maximum age of data in seconds
        :type max_age: `int`
        :returns: ``True`` if data is less than `max_age` old, else ``False``
        :rtype: `Boolean`

        """

        age = self.cached_data_age(name)

        if not age:
            return False

        return age < max_age

    def cached_data_age(self, name):
        """Return age of data cached at `name` in seconds or 0 if
        cache doesn't exist

        :param name: name of datastore
        :type name: ``unicode``
        :returns: age of datastore in seconds
        :rtype: `int`

        """

        cache_path = self.cachefile('%s.%s' % (name, self.cache_serializer))

        if not os.path.exists(cache_path):
            return 0

        return time.time() - os.stat(cache_path).st_mtime

    def filter(self, query, items, key=lambda x: x, ascending=False,
               include_score=False, min_score=0, max_results=0,
               match_on=MATCH_ALL, fold_diacritics=True):
        """Fuzzy search filter. Returns list of ``items`` that match ``query``.

        ``query`` is case-insensitive. Any item that does not contain the
        entirety of ``query`` is rejected.

        :param query: query to test items against
        :type query: ``unicode``
        :param items: iterable of items to test
        :type items: ``list`` or ``tuple``
        :param key: function to get comparison key from ``items``. Must return a
                    ``unicode`` string. The default simply returns the item.
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
            ``rule`` is the ``MATCH_`` rule that matched the item.
        :rtype: ``list``

        **Matching rules**

        By default, :meth:`filter` uses all of the following flags (i.e.
        :const:`MATCH_ALL`). The tests are always run in the given order:

        1. :const:`MATCH_STARTSWITH` : Item search key startswith ``query`` (case-insensitive).
        2. :const:`MATCH_CAPITALS` : The list of capital letters in item search key starts with ``query`` (``query`` may be lower-case). E.g., ``of`` would match ``OmniFocus``, ``gc`` would match ``Google Chrome``
        3. :const:`MATCH_ATOM` : Search key is split into "atoms" on non-word characters (.,-,' etc.). Matches if ``query`` is one of these atoms (case-insensitive).
        4. :const:`MATCH_INITIALS_STARTSWITH` : Initials are the first characters of the above-described "atoms" (case-insensitive).
        5. :const:`MATCH_INITIALS_CONTAIN` : ``query`` is a substring of the above-described initials.
        6. :const:`MATCH_INITIALS` : Combination of (4) and (5).
        7. :const:`MATCH_SUBSTRING` : Match if ``query`` is a substring of item search key (case-insensitive).
        8. :const:`MATCH_ALLCHARS` : Matches if all characters in ``query`` appear in item search key in the same order (case-insensitive).
        9. :const:`MATCH_ALL` : Combination of all the above.


        ``MATCH_ALLCHARS`` is considerably slower than the other tests and
        provides much less accurate results.

        **Examples:**

        To ignore ``MATCH_ALLCHARS`` (tends to provide the worst matches and
        is expensive to run), use ``match_on=MATCH_ALL ^ MATCH_ALLCHARS``.

        To match only on capitals, use ``match_on=MATCH_CAPITALS``.

        To match only on startswith and substring, use
        ``match_on=MATCH_STARTSWITH | MATCH_SUBSTRING``.

        **Diacritic folding**

        .. versionadded:: 1.3

        If ``fold_diacritics`` is ``True`` (the default), and ``query``
        contains only ASCII characters, non-ASCII characters in search keys
        will be converted to ASCII equivalents (e.g. *ü* -> *u*, *ß* -> *ss*,
        *é* -> *e*).

        See :const:`ASCII_REPLACEMENTS` for all replacements.

        If ``query`` contains non-ASCII characters, search keys will not be
        altered.

        """

        # Remove preceding/trailing spaces
        query = query.strip()

        # Use user override if there is one
        fold_diacritics = self.settings.get('__workflows_diacritic_folding',
                                            fold_diacritics)

        results = []

        for i, item in enumerate(items):
            skip = False
            score = 0
            words = [s.strip() for s in query.split(' ')]
            value = key(item).strip()
            if value == '':
                continue
            for word in words:
                if word == '':
                    continue
                s, r = self._filter_item(value, word, match_on,
                                         fold_diacritics)

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
                                (item, score, r)))

        # sort on keys, then discard the keys
        results.sort(reverse=True)
        results = [t[1] for t in results]

        if max_results and len(results) > max_results:
            results = results[:max_results]

        if min_score:
            results = [r for r in results if r[1] > min_score]

        # return list of ``(item, score, rule)``
        if include_score:
            return results
        # just return list of items
        return [t[0] for t in results]

    def _filter_item(self, value, query, match_on, fold_diacritics):
        """Filter ``value`` against ``query`` using rules ``match_on``

        :returns: ``(score, rule)``

        """

        query = query.lower()
        queryset = set(query)

        if not isascii(query):
            fold_diacritics = False

        rule = None
        score = 0

        if fold_diacritics:
            value = self.fold_to_ascii(value)

        # pre-filter any items that do not contain all characters
        # of ``query`` to save on running several more expensive tests
        if not queryset <= set(value.lower()):
            return (0, None)

        # item starts with query
        if (match_on & MATCH_STARTSWITH and
                value.lower().startswith(query)):
            score = 100.0 - (len(value) / len(query))
            rule = MATCH_STARTSWITH

        if not score and match_on & MATCH_CAPITALS:
            # query matches capitalised letters in item,
            # e.g. of = OmniFocus
            initials = ''.join([c for c in value if c in INITIALS])
            if initials.lower().startswith(query):
                score = 100.0 - (len(initials) / len(query))
                rule = MATCH_CAPITALS

        if not score:
            if (match_on & MATCH_ATOM or
                    match_on & MATCH_INITIALS_CONTAIN or
                    match_on & MATCH_INITIALS_STARTSWITH):
                # split the item into "atoms", i.e. words separated by
                # spaces or other non-word characters
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
                    rule = MATCH_ATOM

        if not score:
            # `query` matches start (or all) of the initials of the
            # atoms, e.g. ``himym`` matches "How I Met Your Mother"
            # *and* "how i met your mother" (the ``capitals`` rule only
            # matches the former)
            if (match_on & MATCH_INITIALS_STARTSWITH and
                    initials.startswith(query)):
                score = 100.0 - (len(initials) / len(query))
                rule = MATCH_INITIALS_STARTSWITH

            # `query` is a substring of initials, e.g. ``doh`` matches
            # "The Dukes of Hazzard"
            elif (match_on & MATCH_INITIALS_CONTAIN and
                    query in initials):
                score = 95.0 - (len(initials) / len(query))
                rule = MATCH_INITIALS_CONTAIN

        if not score:
            # `query` is a substring of item
            if match_on & MATCH_SUBSTRING and query in value.lower():
                    score = 90.0 - (len(value) / len(query))
                    rule = MATCH_SUBSTRING

        if not score:
            # finally, assign a score based on how close together the
            # characters in `query` are in item.
            if match_on & MATCH_ALLCHARS:
                search = self._search_for_query(query)
                match = search(value)
                if match:
                    score = 100.0 / ((1 + match.start()) *
                                     (match.end() - match.start() + 1))
                    rule = MATCH_ALLCHARS

        if score > 0:
            return (score, rule)
        return (0, None)

    def _search_for_query(self, query):
        if query in self._search_pattern_cache:
            return self._search_pattern_cache[query]

        # Build pattern: include all characters
        pattern = []
        for c in query:
            # pattern.append('[^{0}]*{0}'.format(re.escape(c)))
            pattern.append('.*?{0}'.format(re.escape(c)))
        pattern = ''.join(pattern)
        search = re.compile(pattern, re.IGNORECASE).search

        self._search_pattern_cache[query] = search
        return search

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

    def add_item(self, title, subtitle='', modifier_subtitles=None, arg=None,
                 autocomplete=None, valid=False, uid=None, icon=None,
                 icontype=None, type=None):
        """Add an item to be output to Alfred

        :param title: Title shown in Alfred
        :type title: ``unicode``
        :param subtitle: Subtitle shown in Alfred
        :type subtitle: ``unicode``
        :param modifier_subtitles: Subtitles shown when modifier
            (CMD, OPT etc.) is pressed. Use a ``dict`` with the lowercase
            keys ``cmd``, ``ctrl``, ``shift``, ``alt`` and ``fn``
        :type modifier_subtitles: ``dict``
        :param arg: Argument passed by Alfred as `{query}` when item is
            actioned
        :type arg: ``unicode``
        :param autocomplete: Text expanded in Alfred when item is TABbed
        :type autocomplete: ``unicode``
        :param valid: Whether or not item can be actioned
        :type valid: `Boolean`
        :param uid: Used by Alfred to remember/sort items
        :type uid: ``unicode``
        :param icon: Filename of icon to use
        :type icon: ``unicode``
        :param icontype: Type of icon. Must be one of ``None`` , ``'filetype'``
           or ``'fileicon'``. Use ``'filetype'`` when ``icon`` is a filetype
           such as``public.folder``. Use ``'fileicon'`` when you wish to
           use the icon of the file specified as ``icon``, e.g.
           ``icon='/Applications/Safari.app', icontype='fileicon'``.
           Leave as `None` if ``icon`` points to an actual
           icon file.
        :type icontype: ``unicode``
        :param type: Result type. Currently only ``'file'`` is supported
            (by Alfred). This will tell Alfred to enable file actions for
            this item.
        :type type: ``unicode``
        :returns: :class:`Item` instance

        """

        item = self.item_class(title, subtitle, modifier_subtitles, arg,
                               autocomplete, valid, uid, icon, icontype, type)
        self._items.append(item)
        return item

    def send_feedback(self):
        """Print stored items to console/Alfred as XML."""
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

        :param account: name of the account the password is for, e.g.
            "Pinboard"
        :type account: ``unicode``
        :param password: the password to secure
        :type password: ``unicode``
        :param service: Name of the service. By default, this is the workflow's
                        bundle ID
        :type service: ``unicode``

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
        """Retrieve the password saved at ``service/account``. Raise
        :class:`PasswordNotFound` exception if password doesn't exist.

        :param account: name of the account the password is for, e.g.
            "Pinboard"
        :type account: ``unicode``
        :param service: Name of the service. By default, this is the workflow's
                        bundle ID
        :type service: ``unicode``
        :returns: account password
        :rtype: ``unicode``

        """

        if not service:
            service = self.bundleid
        retcode, password = self._call_security('find-generic-password',
                                                service, account, '-w')
        self.logger.debug('get_password : %s:%s', service, account)
        return password

    def delete_password(self, account, service=None):
        """Delete the password stored at ``service/account``. Raises
        :class:`PasswordNotFound` if account is unknown.

        :param account: name of the account the password is for, e.g.
            "Pinboard"
        :type account: ``unicode``
        :param service: Name of the service. By default, this is the workflow's
                        bundle ID
        :type service: ``unicode``

        """

        if not service:
            service = self.bundleid
        retcode, output = self._call_security('delete-generic-password',
                                              service, account)
        self.logger.debug('delete_password : %s:%s', service, account)

    ####################################################################
    # Methods for workflow:* magic args
    ####################################################################

    def clear_cache(self):
        """Delete all files in workflow cache directory."""
        self._delete_directory_contents(self.cachedir)

    def clear_data(self):
        """Delete all files in workflow data directory."""
        self._delete_directory_contents(self.datadir)

    def clear_settings(self):
        """Delete settings file."""
        if os.path.exists(self.settings_path):
            os.unlink(self.settings_path)
            self.logger.debug('Deleted : %r', self.settings_path)

    def reset(self):
        """Delete settings, cache and data"""
        self.clear_cache()
        self.clear_data()
        self.clear_settings()

    def open_log(self):
        """Open log file in standard application (usually Console.app)."""
        subprocess.call(['open', self.logfile])  # pragma: no cover

    def open_cachedir(self):
        """Open the workflow cache directory in Finder."""
        subprocess.call(['open', self.cachedir])  # pragma: no cover

    def open_datadir(self):
        """Open the workflow data directory in Finder."""
        subprocess.call(['open', self.datadir])  # pragma: no cover

    def open_workflowdir(self):
        """Open the workflow directory in Finder."""
        subprocess.call(['open', self.workflowdir])  # pragma: no cover

    def open_terminal(self):
        """Open a Terminal window at workflow directory."""
        subprocess.call(['open', '-a', 'Terminal',
                        self.workflowdir])  # pragma: no cover

    ####################################################################
    # Helper methods
    ####################################################################

    def decode(self, text, encoding=None, normalization=None):
        """Return ``text`` as normalised unicode.

        If ``encoding`` and/or ``normalization`` is ``None``, the
        ``input_encoding``and ``normalization`` parameters passed to
        :class:`Workflow` are used.

        :param text: string
        :type text: encoded or Unicode string. If ``text`` is already a
            Unicode string, it will only be normalised.
        :param encoding: The text encoding to use to decode ``text`` to
            Unicode.
        :type encoding: ``unicode`` or ``None``
        :param normalization: The nomalisation form to apply to ``text``.
        :type normalization: ``unicode`` or ``None``
        :returns: decoded and normalised ``unicode``

        :class:`Workflow` uses "NFC" normalisation by default. This is the
        standard for Python and will work well with data from the web (via
        :mod:`~workflow.web` or :mod:`json`).

        OS X, on the other hand, uses "NFD" normalisation (nearly), so data
        coming from the system (e.g. via :mod:`subprocess` or
        :func:`os.listdir`/:mod:`os.path`) may not match. You should either
        normalise this data, too, or change the default normalisation used by
        :class:`Workflow`.

        """

        encoding = encoding or self._input_encoding
        normalization = normalization or self._normalizsation
        if not isinstance(text, unicode):
            text = unicode(text, encoding)
        return unicodedata.normalize(normalization, text)

    def fold_to_ascii(self, text):
        """
        .. versionadded:: 1.3

        Convert non-ASCII characters to closest ASCII equivalent.

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

    def _delete_directory_contents(self, dirpath):
        """Delete all files in a directory

        :param dirpath: path to directory to clear
        :type dirpath: ``unicode`` or ``str``

        """

        if os.path.exists(dirpath):
            for filename in os.listdir(dirpath):
                path = os.path.join(dirpath, filename)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
                self.logger.debug('Deleted : %r', path)

    def _load_info_plist(self):
        """Load workflow info from ``info.plist``

        """

        self._info = plistlib.readPlist(self._info_plist)
        self._info_loaded = True

    def _create(self, dirpath):
        """Create directory `dirpath` if it doesn't exist

        :param dirpath: path to directory
        :type dirpath: ``unicode``
        :returns: ``dirpath`` argument
        :rtype: ``unicode``

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
        :type action: ``unicode``
        :param service: Name of the service.
        :type service: ``unicode``
        :param account: name of the account the password is for, e.g.
            "Pinboard"
        :type account: ``unicode``
        :param password: the password to secure
        :type password: ``unicode``
        :param *args: list of command line arguments to be passed to
                      ``security``
        :type *args: `list` or `tuple`
        :returns: ``(retcode, output)``. ``retcode`` is an `int`, ``output`` a
                  ``unicode`` string.
        :rtype: `tuple` (`int`, ``unicode``)

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
