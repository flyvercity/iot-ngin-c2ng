# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import os
import pytest
from datetime import datetime

import test_utils as u

UAS_ID = os.getenv('C2NG_SIM_DRONE_ID')


@pytest.fixture(scope='module')
def with_ua_session():
    ua_session_info = u.auth_request('POST', '/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': UAS_ID,
        'Segment': 'ua',
        'IMSI': '123456789012345',
    })

    yield ua_session_info

    # TODO: delete session


@pytest.fixture(scope='module')
def with_adx_session():
    adx_session_info = u.auth_request('POST', '/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': UAS_ID,
        'Segment': 'adx',
    })

    yield adx_session_info

    # TODO: delete session


def test_ua_session_init(with_ua_session):
    ua_session_info = with_ua_session
    assert 'IP' in ua_session_info
    assert 'GatewayIP' in ua_session_info
    assert 'KID' in ua_session_info


def test_adx_session_init(with_adx_session):
    adx_session_info = with_adx_session
    assert 'IP' in adx_session_info
    assert 'GatewayIP' in adx_session_info
    assert 'KID' in adx_session_info


def test_ua_peer_address(with_ua_session):
    address_info = u.auth_request('GET', f'/address/{UAS_ID}/ua')
    assert address_info['Address'] == with_ua_session['IP']


def test_adx_peer_address(with_adx_session):
    address_info = u.auth_request('GET', f'/address/{UAS_ID}/adx')
    assert address_info['Address'] == with_adx_session['IP']


def test_peer_public_key(with_ua_session):
    public_key_info = u.auth_request('GET', f'/certificate/{UAS_ID}/ua')
    assert public_key_info['KID'] == with_ua_session['KID']


def test_peer_public_key_adx(with_adx_session):
    public_key_info_adx = u.auth_request('GET', f'/certificate/{UAS_ID}/adx')
    assert public_key_info_adx['KID'] == with_adx_session['KID']
