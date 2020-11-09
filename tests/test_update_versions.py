#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#

"""Test `update.Version` class."""



import unittest

import pytest

from workflow.update import Version


class VersionTests(unittest.TestCase):
    """Unit tests for Version."""

    def setUp(self):
        """Initialise unit test data."""
        self.invalid_versions = [
            '',
            'bob',
            '1.x.8',
            '1.0b',
            '1.0.3a',
            '1.0.0.0',
            '1.2.3.4',
            'v.1.1',
            '.1.2.1',
        ]
        self.valid_versions = [
            ('1', '1.0.0'),
            ('1.9', '1.9.0'),
            ('10.0', '10.0.0'),
            '1.0.1',
            '2.2.1',
            '10.11.12',
            '9.99.9999',
            '12.333.0-alpha',
            '8.10.11',
            '9.4.3+20144353453',
            '3.1.4-beta+20144334',
        ]

    def test_invalid_versions(self):
        """Versions: invalid versions"""
        for v in self.invalid_versions:
            self.assertRaises(ValueError, Version, v)

    def test_valid_versions(self):
        """Versions: valid versions"""
        for v in self.valid_versions:
            if isinstance(v, tuple):
                vin, vout = v
            else:
                vin = vout = v
            self.assertEqual(str(Version(vin)), vout)
            self.assertEqual(str(Version('v{0}'.format(vin))), vout)

    def test_compare_bad_objects(self):
        """Versions: invalid comparisons"""
        v = Version('1.0.0')
        t = (1, 0, 0)
        self.assertRaises(ValueError, lambda v, t: v == t, v, t)
        self.assertRaises(ValueError, lambda v, t: v >= t, v, t)
        self.assertRaises(ValueError, lambda v, t: v <= t, v, t)
        self.assertRaises(ValueError, lambda v, t: v != t, v, t)
        self.assertRaises(ValueError, lambda v, t: v > t, v, t)
        self.assertRaises(ValueError, lambda v, t: v < t, v, t)

    def test_compare_versions(self):
        """Versions: comparisons"""
        self.assertTrue(Version('1') == Version('1.0') == Version('1.0.0'))
        self.assertTrue(Version('1.0.0') == Version('01.0.00'))
        self.assertTrue(Version('1.10.0') > Version('1.9.9'))
        self.assertTrue(Version('1.10.0') > Version('1.10.0-alpha'))
        self.assertTrue(Version('1.9.9') < Version('1.10.0'))
        self.assertTrue(Version('1.10.0-alpha') < Version('1.10.0'))
        self.assertTrue(Version('1.10.0') >= Version('1.9.9'))
        self.assertTrue(Version('1.10.0') >= Version('1.10.0-alpha'))
        self.assertTrue(Version('1.9.9') <= Version('1.10.0'))
        self.assertTrue(Version('1.10.0-alpha') <= Version('1.10.0'))
        self.assertTrue(Version('1.10.0-alpha') < Version('1.10.0-beta'))
        self.assertTrue(Version('1.10.0-beta') > Version('1.10.0-alpha'))
        self.assertTrue(Version('1.10.0-beta') != Version('1.10.0-alpha'))
        self.assertTrue(Version('1.10.0-alpha') != Version('1.10.0'))
        self.assertTrue(Version('2.10.20') > Version('1.20.30'))
        self.assertTrue(Version('2.10.20') == Version('2.10.20+2342345345'))
        # With v prefix
        self.assertTrue(Version('v1.0.0') == Version('01.0.00'))
        self.assertTrue(Version('v1.10.0') > Version('1.9.9'))
        self.assertTrue(Version('v1.10.0') > Version('1.10.0-alpha'))
        self.assertTrue(Version('v1.9.9') < Version('1.10.0'))
        self.assertTrue(Version('v1.10.0-alpha') < Version('1.10.0'))
        self.assertTrue(Version('v1.10.0') >= Version('1.9.9'))
        self.assertTrue(Version('v1.10.0') >= Version('1.10.0-alpha'))
        self.assertTrue(Version('v1.9.9') <= Version('1.10.0'))
        self.assertTrue(Version('v1.10.0-alpha') <= Version('1.10.0'))
        self.assertTrue(Version('v1.10.0-alpha') < Version('1.10.0-beta'))
        self.assertTrue(Version('v1.10.0-beta') > Version('1.10.0-alpha'))
        self.assertTrue(Version('v1.10.0-beta') != Version('1.10.0-alpha'))
        self.assertTrue(Version('v1.10.0-alpha') != Version('1.10.0'))
        self.assertTrue(Version('v2.10.20') > Version('1.20.30'))
        self.assertTrue(Version('v2.10.20') == Version('2.10.20+2342345345'))
        # With and without suffixes
        self.assertTrue(Version('v1.10.0') > Version('1.10.0-beta'))
        self.assertTrue(Version('v1.10.0-alpha') < Version('1.10.0-beta'))
        # Complex suffixes
        self.assertTrue(Version('1.0.0-alpha') < Version('1.0.0-alpha.1'))
        self.assertTrue(Version('1.0.0-alpha.1') < Version('1.0.0-alpha.beta'))
        self.assertTrue(Version('1.0.0-alpha.beta') < Version('1.0.0-beta'))
        self.assertTrue(Version('1.0.0-beta') < Version('1.0.0-beta.2'))
        self.assertTrue(Version('1.0.0-beta.2') < Version('1.0.0-beta.11'))
        self.assertTrue(Version('1.0.0-beta.11') < Version('1.0.0-rc.1'))
        self.assertTrue(Version('1.0.0-rc.1') < Version('1.0.0'))


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
