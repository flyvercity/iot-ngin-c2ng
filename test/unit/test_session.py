# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import os
from datetime import datetime

import test_utils as u

UAS_ID = os.getenv('C2NG_SIM_DRONE_ID')


def test_session_init():
    adx_session_info = u.auth_request('POST', '/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': UAS_ID,
        'Segment': 'ua'
    })

    print(adx_session_info)
    assert False
