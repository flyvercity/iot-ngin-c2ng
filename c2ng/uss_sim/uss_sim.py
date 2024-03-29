# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI USSP Endpoint Simulator.'''
import os
import logging as lg
import asyncio
from argparse import ArgumentParser
import json

import requests
import tornado.web as web
from jose import jwk, jwt


class AuthHandler(web.RequestHandler):
    '''Base for all handlers for authenticated requests.'''

    def prepare(self):
        super().prepare()
        self.get_current_user()

    def get_current_user(self):
        '''Using this method for authentication.

        Raises:
            HTTPError: if authentication fails.
        '''

        try:
            auth_header = self.request.headers.get('Authentication', '')

            if len(auth_header.split()) < 2:
                raise web.HTTPError(401, reason='Unauthorized')

            bearer = auth_header.split()[1]

            if not auth_header or not bearer:
                raise web.HTTPError(401, reason='Unauthorized')

            base = self.settings['authserver']
            wkurl = f'{base}/realms/c2ng/protocol/openid-connect/certs'
            print(wkurl)
            wkinfo = requests.get(wkurl).json()
            sig_keys = filter(lambda key: key['use'] == 'sig', wkinfo['keys'])
            public_key = jwk.construct(next(sig_keys))

            payload = jwt.decode(
                bearer, public_key,
                algorithms='RS256', options={'verify_aud': False}
            )

            lg.info(f'Service authorized: {payload["clientHost"]}')
        except Exception as exc:
            lg.warning(f'Authentication failed: {exc}')
            raise web.HTTPError(403, reason=str(exc))


class ApproveHandler(AuthHandler):
    '''Simulate flight approve endpoint.'''

    def get(self):
        '''Returns approval or disapproval.'''
        self.get_current_user()
        self.set_header('Content-Type', 'application/json')
        uasid = self.get_argument('UasID')
        lg.info(f'Approving connection for {uasid}')

        data = {
            'UasID': uasid,
            'Approved': not self.settings['disapprove']
        }

        self.finish(json.dumps(data) + '\n')


def handlers():
    '''Returns a full set of URLSpec.

    Returns:
        A list of URL specifications.
    '''

    return [
        (r'/approve', ApproveHandler),
    ]


async def run(args: dict):
    '''Simulator async entry point.

    Args:
        args: command line parameters
    '''

    port = args.port

    app = web.Application(
        handlers(),
        authserver=args.auth,
        disapprove=args.disapprove
    )

    lg.info(f'USS SIM :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


async def main():
    C2NG_DEFAULT_USS_PORT = os.getenv('C2NG_DEFAULT_USS_PORT')

    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('-p', '--port', type=int, default=C2NG_DEFAULT_USS_PORT)
    parser.add_argument('-D', '--disapprove', action='store_true', default=False)

    parser.add_argument(
        '-a', '--auth', help='Address of the OIDC server (by default, KeyCloak)',
        default='http://oauth:8080/'
    )

    args = parser.parse_args()
    lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)
    await run(args)


if __name__ == '__main__':
    asyncio.run(main())
