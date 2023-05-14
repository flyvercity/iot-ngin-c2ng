#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''UA and RPR Simulators'''

from datetime import datetime


DEFAULT_SAFETY_MARGIN = 300


def post(ctx, path, query):
    response = ctx.request(path, method='POST', body=query)
    ctx.dump(response)


def request_ua(ctx):
    post(ctx, '/ua/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': ctx.args.uasid,
        'IMSI': '123456989012345'
    })


def request_adx(ctx):
    post(ctx, '/adx/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': ctx.args.uasid,
    })
