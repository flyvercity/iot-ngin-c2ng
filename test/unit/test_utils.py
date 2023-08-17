# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import os

import requests
from keycloak import KeycloakOpenID


AUTH_URL = 'http://oauth:8080/'
SERVICE_URL = 'http://c2ng:9090'
UAS_ID = os.getenv('C2NG_SIM_DRONE_ID')
UAS_PASSWORD = os.getenv('C2NG_UA_DEFAULT_PASSWORD')
UAS_SECRET = os.getenv('C2NG_UAS_CLIENT_SECRET')


def auth_request(method: str, path: str, body={}, qsp={}) -> dict:
    '''Make a authenticated request to the service.

    Args:
        method: HTTP method.
        path: relative endpoint path.
        body: JSON object for call payload.
        qsp: a dict with query string parameters.

    Returns:
        Response as a JSON object.

    Raises:
        UserWarning: when server's response is malformed.
    '''

    print(f'CREDS [{AUTH_URL}], [{UAS_ID}], [{UAS_PASSWORD}], [{UAS_SECRET}]')

    keycloak_openid = KeycloakOpenID(
        server_url=AUTH_URL,
        realm_name="c2ng",
        client_id="c2-access",
        client_secret_key=UAS_SECRET
    )

    token = keycloak_openid.token(UAS_ID, UAS_PASSWORD)
    print('KeyCloak token received')
    access_token = token['access_token']
    headers = {'Authentication': f'Bearer {access_token}'}
    url = SERVICE_URL + path
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

    return reply
