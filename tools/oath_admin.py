# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI Tools to manage the KeyCloak OAuth service.'''
import os

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from dotenv import load_dotenv


load_dotenv()


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

    uss_access_def = {
        'clientId': 'uss-access',
        'enabled': True,
        "clientAuthenticatorType": "client-secret",
        "secret": os.getenv('C2NG_USS_CLIENT_SECRET'),
        'standardFlowEnabled': False,
        'implicitFlowEnabled': False,
        'directAccessGrantsEnabled': False,
        'serviceAccountsEnabled': True,
        'publicClient': False,
        'protocol': 'openid-connect'
    }

    admin.create_client(uss_access_def, skip_exists=True)

    # TODO: remove demo user on default
    droneid_def = {
        'username': os.getenv('C2NG_SIM_DRONE_ID'),
        'enabled': True,
        'credentials': [
            {
                'value': os.getenv('C2NG_UA_DEFAULT_PASSWORD'),
                'type': 'password'
            }
        ]
    }

    admin.create_user(droneid_def, exist_ok=True)


def add_arg_subparsers(sp):
    keycloak = sp.add_parser('keycloak', help='OAuth service administration tool')

    keycloak.add_argument(
        '-u', '--user', help='KeyCloak administrator user',
        default=os.getenv('KEYCLOAK_ADMIN')
    )

    keycloak.add_argument(
        '-p', '--password', help='KeyCloak authentication password',
        default=os.getenv('KEYCLOAK_ADMIN_PASSWORD')
    )
