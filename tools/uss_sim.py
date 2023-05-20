# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI USSP Endpoint Simulator.'''
import logging as lg
import json
import asyncio

import requests
import tornado.web as web
from jose import jwk, jwt


class AuthHandler(web.RequestHandler):
    '''Base for all handlers for authenticated requests.'''

    def prepare(self):
        super().prepare()
        self.get_current_user()

    def get_current_user(self):
        '''Using this method for authentication.'''

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
            lg.warn(f'Authentication failed: {exc}')
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
    '''Returns a full set of URLSpec'''

    return [
        (r'/approve', ApproveHandler),
    ]


async def start(args: dict):
    '''Simulator async entry point.

    Args:
    - `args`: command line parameters
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


def run(args):
    '''Simulator sync entry point.'''
    asyncio.run(start(args))
