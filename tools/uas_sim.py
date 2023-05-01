#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''UAV and RPR Simulators'''

from datetime import datetime


DEFAULT_SAFETY_MARGIN = 300


def request(ctx):
    query = {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': ctx.args.uasid,
        'IMSI': '123456989012345'
    }

    response = ctx.request('/uav/session', method='POST', body=query)
    ctx.dump(response)
