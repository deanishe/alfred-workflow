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

import json
import os


class PersistentDict(dict):
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

        super(PersistentDict, self).__init__()
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
        with open(self._filepath, 'rb') as file_obj:
            for key, value in json.load(file_obj, encoding='utf-8').items():
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
        with open(self._filepath, 'wb') as file_obj:
            json.dump(data, file_obj, sort_keys=True, indent=2,
                      encoding='utf-8')

    # dict methods
    def __setitem__(self, key, value):
        super(PersistentDict, self).__setitem__(key, value)
        self.save()

    def __delitem__(self, key):
        super(PersistentDict, self).__delitem__(key)
        self.save()

    def update(self, *args, **kwargs):
        """Override :class:`dict` method to save on update."""
        super(PersistentDict, self).update(*args, **kwargs)
        self.save()

    def setdefault(self, key, value=None):
        """Override :class:`dict` method to save on update."""
        ret = super(PersistentDict, self).setdefault(key, value)
        self.save()
        return ret
