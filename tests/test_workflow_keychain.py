# encoding: utf-8
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
# MIT Licence applies http://opensource.org/licenses/MIT
#
# Created 2019-05-05

"""Unit tests for Keychain API."""



import pytest

from workflow.workflow import PasswordNotFound, KeychainError

from .conftest import BUNDLE_ID


ACCOUNT = 'this-is-my-test-account'
PASSWORD = 'hunter2'
PASSWORD2 = 'hunter2ing'
PASSWORD3 = 'hünter\\“2”'


def test_keychain(wf):
    """Save/get/delete password"""
    # ensure password is unset
    try:
        wf.delete_password(ACCOUNT)
    except PasswordNotFound:
        pass

    with pytest.raises(PasswordNotFound):
        wf.delete_password(ACCOUNT)
    with pytest.raises(PasswordNotFound):
        wf.get_password(ACCOUNT)

    wf.save_password(ACCOUNT, PASSWORD)
    assert wf.get_password(ACCOUNT) == PASSWORD
    assert wf.get_password(ACCOUNT, BUNDLE_ID)

    # set same password
    wf.save_password(ACCOUNT, PASSWORD)
    assert wf.get_password(ACCOUNT) == PASSWORD

    # set different password
    wf.save_password(ACCOUNT, PASSWORD2)
    assert wf.get_password(ACCOUNT) == PASSWORD2

    # set non-ASCII password
    wf.save_password(ACCOUNT, PASSWORD3)
    assert wf.get_password(ACCOUNT) == PASSWORD3

    # bad call to _call_security
    with pytest.raises(KeychainError):
        wf._call_security('pants', BUNDLE_ID, ACCOUNT)
