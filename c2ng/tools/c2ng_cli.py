# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI Tools to manage the Service and simulators.'''
from argparse import ArgumentParser

from dotenv import load_dotenv

import c2ng.common.c2ng_util as u
import c2ng.tools.oath_admin as oath_admin
import c2ng.tools.gen_openapi as gen_openapi
import c2ng.tools.crypto_keys as crypto_keys


class Handler:
    '''Command dispatcher.'''

    def __init__(self, args):
        self._args = args

    def handle(self):
        '''Dispatch a CLI command.'''

        try:
            func = getattr(self, self._args.command)
            func()

        except UserWarning as exc:
            print(f'Command failed: {exc}')

    def keycloak(self):
        '''Configure the KeyCloak service.'''
        oath_admin.run(self._args)

    def genapi(self):
        '''Generate OpenAPI specification.'''
        gen_openapi.run(self._args)

    def cryptokeys(self):
        '''Generate crypto keys.'''
        crypto_keys.run(self._args)


def main():
    '''C2NG CLI Tool entry point.'''

    load_dotenv()

    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    parser.add_argument(
        '-a', '--auth', help='Address of the OIDC server (by default, KeyCloak)',
        default='http://localhost:8080/'
    )

    sp = parser.add_subparsers(dest='command', required=True, metavar='CMD')
    oath_admin.add_arg_subparsers(sp)
    gen_openapi.add_arg_subparsers(sp)
    crypto_keys.add_arg_subparsers(sp)
    args = parser.parse_args()
    u.setup_logging(args.verbose)
    Handler(args).handle()


if __name__ == '__main__':
    main()
