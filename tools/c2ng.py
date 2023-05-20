# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI Tools to manage the Service and simulators'''
import os
import logging as lg
from argparse import ArgumentParser

from dotenv import load_dotenv

import uas_sim
import uss_sim
import oath_admin as oath_admin


DEFAULT_USS_PORT = 9091
'''Default port for the USS simulator'''


class Handler:
    '''Command dispatcher'''

    def __init__(self, args):
        self.args = args

    def handle(self):
        '''Dispatch a CLI command'''

        try:
            func = getattr(self, self.args.command)
            func()

        except UserWarning as exc:
            print(f'Command failed: {exc}')

    def ua(self):
        '''Simulate a request on behalf of a drone'''
        uas_sim.request_ua(self.args)

    def adx(self):
        '''Simulate a request on behalf of a ground element (e.g., RPS)'''
        uas_sim.request_adx(self.args)

    def uss(self):
        '''Start USS simulator'''
        uss_sim.run(self.args)

    def keycloak(self):
        '''Configure the KeyCloak service'''
        oath_admin.configure_oauth(self.args)


def main():
    '''C2NG CLI Tool entry point.'''
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    parser.add_argument(
        '-u', '--url', help='C2NG service URL',
        default='http://localhost:9090'
    )

    parser.add_argument(
        '-a', '--auth', help='Address of the OIDC server (by default, KeyCloak)',
        default='http://localhost:8080/'
    )

    sp = parser.add_subparsers(dest='command', required=True, metavar='CMD')
    sp.add_parser('test', help='Test a connection with the service')

    ua = sp.add_parser('ua', help='Command on behalf of UA')
    ua.add_argument('-i', '--uasid', help='UAS CAA ID', default='droneid')

    ua.add_argument(
        '-p', '--password', help='UA OIDC Authentication password',
        default=os.getenv('C2NG_UA_DEFAULT_PASSWORD')
    )

    adx = sp.add_parser('adx', help='Command on behalf of UA')
    adx.add_argument('-i', '--uasid', help='UAS CAA ID', default='droneid')

    adx.add_argument(
        '-p', '--password', help='ADX OIDC Authentication password',
        default=os.getenv('C2NG_ADX_DEFAULT_PASSWORD')
    )

    uss = sp.add_parser('uss', help='USSP Simulator')
    uss.add_argument('-p', '--port', type=int, default=DEFAULT_USS_PORT)
    uss.add_argument('-D', '--disapprove', action='store_true', default=False)

    keycloak = sp.add_parser('keycloak', help='OAuth service administration tool')

    keycloak.add_argument(
        '-u', '--user', help='KeyCloak administrator user',
        default=os.getenv('KEYCLOAK_ADMIN')
    )

    keycloak.add_argument(
        '-p', '--password', help='KeyCloak authentication password',
        default=os.getenv('KEYCLOAK_ADMIN_PASSWORD')
    )

    args = parser.parse_args()
    lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)
    Handler(args).handle()


if __name__ == '__main__':
    load_dotenv()
    main()
