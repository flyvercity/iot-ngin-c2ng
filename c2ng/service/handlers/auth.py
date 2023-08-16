# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module handles API authentication against OAuth.'''
import logging as lg
import asyncio

import requests
from tornado import web
from jose import jwt, jwk

from c2ng.service.handlers.base import HandlerBase


async def fetch_keycloak_public_certs(config):
    keycloak = config['oauth']['keycloak']
    lg.info('Fetching KeyCloak public keys started')

    while True:
        try:
            base = keycloak['base']
            realm = keycloak['realm']
            wkurl = f'{base}/realms/{realm}/protocol/openid-connect/certs'
            lg.info(f"Fetching KeyCloak public keys: {wkurl}")
            config['wkinfo'] = requests.get(wkurl).json()
            return

        except Exception as exc:
            lg.warning(f'Exception while fetching KeyCloak public keys: {exc}')
            lg.info('Unable to fetch KeyCloak keys, re-trying...')
            timeout = keycloak['retry-timeout']
            lg.debug(f'Waiting {timeout} seconds before retrying')
            await asyncio.sleep(timeout)


class AuthHandler(HandlerBase):
    '''Base for all handlers for authenticated requests.'''

    def prepare(self):
        '''Authenticate on request prepare.'''
        super().prepare()
        self._current_user = self.get_current_user()

    def get_current_user(self):
        '''Using this method for authentication.

        Returns:
            User's JWT token payload.
        '''

        wkinfo = self.settings['config']['wkinfo']
        auth_header = self.request.headers.get('Authentication', '')
        return get_auth_user(wkinfo, auth_header)


def get_auth_user(wkinfo, auth_header):
    try:
        if len(auth_header.split()) < 2:
            raise web.HTTPError(401, reason='Unauthorized')

        bearer = auth_header.split()[1]

        if not auth_header or not bearer:
            raise web.HTTPError(401, reason='Unauthorized')

        sig_keys = filter(lambda key: key['use'] == 'sig', wkinfo['keys'])
        public_key = jwk.construct(next(sig_keys))

        payload = jwt.decode(
            bearer, public_key,
            algorithms='RS256', options={'verify_aud': False}
        )

        lg.debug(f'User authorized: {payload["preferred_username"]}')
        return payload

    except Exception as exc:
        lg.warning(f'Authentication failed: {exc}')
        raise web.HTTPError(403, reason=str(exc))
