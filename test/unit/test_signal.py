# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import os
from datetime import datetime

import test_utils as u


UAS_ID = os.getenv('C2NG_SIM_DRONE_ID')


def test_signal_report():
    u.auth_request('POST', '/signal', body={
        'UasID': 'test_uas_id',
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
