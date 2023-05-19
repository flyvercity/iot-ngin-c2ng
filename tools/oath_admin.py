#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''CLI Tools to manage the KeyCloak OAuth service'''
import os

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection


def configure_oauth(args: dict):
    '''Creates a realm, clients and sets up other authentication parameters.

    Args:
    - args: command line args
    '''

    conn = KeycloakOpenIDConnection(
        server_url=args.auth,
        username=args.user,
        password=args.password,
        realm_name="master"
    )

    admin = KeycloakAdmin(connection=conn)

    realm_def = {
        'realm': 'c2ng',
        'enabled': True
    }

    admin.create_realm(realm_def, skip_exists=True)
    admin.realm_name = 'c2ng'

    c2_access_def = {
        'clientId': 'c2-access',
        'enabled': True,
        "clientAuthenticatorType": "client-secret",
        "secret": os.getenv('C2NG_UAS_CLIENT_SECRET'),
        'standardFlowEnabled': False,
        'implicitFlowEnabled': False,
        'directAccessGrantsEnabled': True,
        'serviceAccountsEnabled': False,
        'publicClient': False,
        'protocol': 'openid-connect'
    }

    admin.create_client(c2_access_def, skip_exists=True)

    droneid_def = {
        'username': 'droneid',
        'enabled': True,
        'credentials': [
            {
                'value': os.getenv('C2NG_UA_DEFAULT_PASSWORD'),
                'type': 'password'
            }
        ]
    }

    # TODO: remove demo user on default
    admin.create_user(droneid_def, exist_ok=True)