#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''This handles API authentication against KeyCloak'''
import logging as lg

import requests
import tornado.web as web
from jose import jwk, jwt

from handlers.base import HandlerBase


class AuthHandler(HandlerBase):
    '''Base for all handlers for authenticated requests'''

    def get_current_user(self):
        '''Using this method for authentication'''

        try:
            auth_header = self.request.headers.get('Authorization', '')

            if len(auth_header.split(' ')) < 2:
                raise web.HTTPError(401, reason='Unauthorized')

            bearer = auth_header.split(' ')[1]
            if not auth_header or not bearer:
                raise web.HTTPError(401, reason='Unauthorized')

        except Exception as exc:
            raise web.HTTPError(403, reason=str(exc))

        config = self.settings['config']['keycloak']
        base = config['base']
        realm = config['realm']
        wkurl = f'{base}/realms/{realm}/protocol/openid-connect/certs'
        wkinfo = requests.get(wkurl)
        public_key = jwk.construct(wkinfo['keys'][0])

        payload = jwt.decode(
            bearer, public_key,
            algorithms='RS256', options={'verify_aud': False}
        )

        lg.info(f'User authorized: {payload}')
