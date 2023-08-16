# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines the USSP interface.'''
import os
import logging as lg
from typing import Tuple

import requests  # TODO: asynchronize it
from keycloak import KeycloakOpenID


class UssInterface:
    '''USSP API Implementation'''
    def __init__(self, config) -> None:
        '''Constructor.

        Args:
            config: the `uss` section of the configuration file.
        '''

        self.config = config

    def request(self, uasid) -> Tuple[bool, str]:
        '''Requests a flight authorization for the USSP.

        Args:
            uasid: Logical UAS identifier.

        Returns:
            A tuple with a boolean authorization flag and an error string (if any).
        '''

        try:
            oauth = self.config['oauth']['keycloak']

            openid = KeycloakOpenID(
                server_url=oauth['base'],
                realm_name=oauth['realm'],
                client_id=oauth['auth-client-id'],
                client_secret_key=os.getenv('C2NG_USS_CLIENT_SECRET')
            )

            token = openid.token(grant_type='client_credentials')
            access_token = token['access_token']
            headers = {'Authentication': f'Bearer {access_token}'}
            url = f"{self.config['endpoint']}/approve?UasID={uasid}"
            lg.info(f'Approving request from {uasid}')
            lg.debug(f'USS Request URL: {url}')
            answer = requests.get(url, headers=headers)
            answer.raise_for_status()
            response = answer.json()
            approved = response['Approved']
            return (approved, None)

        except Exception as exc:
            lg.warning(f'USSP request failed: {exc}')
            return (None, 'Request failed')
