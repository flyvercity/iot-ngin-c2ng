# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import test_utils as u


UAS_ID = 'sim-drone-id'


def test_get_jwt():
    jwt = u.auth_request('GET', f'/did/jwt/{UAS_ID}')
    assert 'JWT' in jwt


def test_get_verifier_config():
    config = u.auth_request('GET', f'/did/config/{UAS_ID}')
    assert 'Config' in config
