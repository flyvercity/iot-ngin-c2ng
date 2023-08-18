# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import os
from datetime import datetime

import pytest

import test_utils as u


# NB: Using surrogate UAS ID to avoid polluting the database.
UAS_ID = 'test_uas_id'


@pytest.fixture(scope='module')
def with_signal_report():
    u.auth_request('POST', f'/signal/{UAS_ID}', body={
        'Packet': {
            'timestamp': {
                'unix': datetime.now().timestamp(),
            },
            'position': {
                'location': {
                    'lat': 35.0,
                    'lon': 35.0,
                    'alt': 100.0
                }
            },
            'signal': {
                'radio': '5GNSA',
                'RSRP': -99,
                'RSRQ': -99,
                'RSSI': -99,
                'SINR': -99
            },
            'perf': {
                'heartbeat_loss': False,
                'RTT': 2.0
            }
        }
    })


def test_signal_report(with_signal_report):
    pass


def test_get_signal_stats(with_signal_report):
    stats = u.auth_request('GET', f'/signal/{UAS_ID}')
    print('STATS', stats)
    assert False
