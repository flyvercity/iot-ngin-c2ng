# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI UA and RPS Simulators.'''
import os
from datetime import datetime

import requests

import toolutil as u
from keycloak import KeycloakOpenID


def request(args, method: str, path: str, body={}, qsp={}) -> dict:
    keycloak_openid = KeycloakOpenID(
        server_url=args.auth,
        realm_name="c2ng",
        client_id="c2-access",
        client_secret_key=os.getenv('C2NG_UAS_CLIENT_SECRET')
    )

    token = keycloak_openid.token("droneid", args.password)
    access_token = token['access_token']
    headers = {'Authentication': f'Bearer {access_token}'}
    url = args.url + path
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

    u.pprint(reply)


def request_ua(args: dict):
    request(args, 'POST', '/ua/session', body={
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': args.uasid,
        'IMSI': '123456989012345'
    })

    request(args, 'GET', f'/certificate/adx/{args.uasid}')


def request_adx(args: dict):
    request(args, 'POST', '/adx/session', {
        'ReferenceTime': datetime.now().timestamp(),
        'UasID': args.uasid,
    })

    request(args, 'GET', f'/certificate/ua/{args.uasid}')
