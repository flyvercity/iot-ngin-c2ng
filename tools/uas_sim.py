#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''UA and RPR Simulators'''
import os
import json
from datetime import datetime

import requests
from keycloak import KeycloakOpenID
from pygments import highlight
from pygments.lexers.jsonnet import JsonnetLexer
from pygments.formatters import TerminalFormatter


def dump(data):
    json_str = json.dumps(data, indent=4, sort_keys=True)
    print(highlight(json_str, JsonnetLexer(), TerminalFormatter()))


def request(ctx, method: str, path: str, body={}, qsp={}) -> dict:
    keycloak_openid = KeycloakOpenID(
        server_url=ctx.args.auth,
        realm_name="c2ng",
        client_id="c2-access",
        client_secret_key=os.getenv('C2NG_UAS_CLIENT_SECRET')
    )

    token = keycloak_openid.token("droneid", ctx.args.password)
    access_token = token['access_token']
    headers = {'Authentication': f'Bearer {access_token}'}
    url = ctx.args.url + path
    r = requests.request(method=method, url=url, json=body, params=qsp, headers=headers)
    reply = r.json()

    if 'Success' not in reply:
        raise UserWarning(f'Malformed reply: {r.text}')

    if not reply['Success']:
        if 'Errors' not in reply:
            raise UserWarning(f'Malformed failure reply: {r.text}')

        errors = reply['Errors']

        if message := reply.get('Message'):
            print(f'Error message from service: {message}')

        raise UserWarning(errors)

    dump(reply)


def request_ua(ctx):
    request(ctx, 'POST', '/ua/session', body={
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': ctx.args.uasid,
        'IMSI': '123456989012345'
    })

    request(ctx, 'GET', f'/certificate/adx/{ctx.args.uasid}')


def request_adx(ctx):
    request(ctx, 'POST', '/adx/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': ctx.args.uasid,
    })

    request(ctx, 'GET', f'/certificate/ua/{ctx.args.uasid}')
