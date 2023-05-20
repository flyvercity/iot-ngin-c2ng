# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module handles API authentication against OAuth.'''
import logging as lg

import requests
import tornado.web as web
from jose import jwk, jwt

from handlers.base import HandlerBase


class AuthHandler(HandlerBase):
    '''Base for all handlers for authenticated requests'''

    def prepare(self):
        super().prepare()
        self.get_current_user()

    def get_current_user(self):
        '''Using this method for authentication'''

        try:
            auth_header = self.request.headers.get('Authentication', '')

            if len(auth_header.split()) < 2:
                raise web.HTTPError(401, reason='Unauthorized')

            bearer = auth_header.split()[1]

            if not auth_header or not bearer:
                raise web.HTTPError(401, reason='Unauthorized')

            config = self.settings['config']['oauth']['keycloak']
            base = config['base']
            realm = config['realm']
            # TODO: cache these
            wkurl = f'{base}/realms/{realm}/protocol/openid-connect/certs'
            wkinfo = requests.get(wkurl).json()
            sig_keys = filter(lambda key: key['use'] == 'sig', wkinfo['keys'])
            public_key = jwk.construct(next(sig_keys))

            payload = jwt.decode(
                bearer, public_key,
                algorithms='RS256', options={'verify_aud': False}
            )

            lg.info(f'User authorized: {payload["preferred_username"]}')
        except Exception as exc:
            lg.warn(f'Authentication failed: {exc}')
            raise web.HTTPError(403, reason=str(exc))
