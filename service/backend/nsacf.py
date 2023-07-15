# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements an interface with Network Slice Admission Control Function.'''


class NSACF:
    '''NSACF API Implementation.'''

    def __init__(self, config: dict):
        '''Constructor.

        Args:
            config: contains `nsacf` section of the configuration file.
        '''

        self._config = config

    def get_ue_network_creds(self, imsi: str):
        '''Get next network credentials for a UE.

        Args:
            imsi: unique UE identifier.

        Returns:
            JSON object::

                {
                    "IP": "<address>",
                    "Gateway": "<address>"
                }

        Raises:
            RuntimeError: if NSACF endpoint is not implemented
        '''

        if self._config.get('simulated'):
            return {
                'IP': '127.0.0.1',
                'Gateway': '127.0.0.1'
            }

        raise RuntimeError('Not implemented exception')

    def get_adx_network_creds(self, uid: str):
        '''Get next network credentials for an ADX client.

        Args:
            uid: unique ID

        Returns:
            JSON object::

                {
                    "IP": "<address>",
                    "Gateway": "<address>"
                }

        Raises:
            RuntimeError: if NSACF endpoint is not implemented

        '''

        if self._config.get('simulated'):
            return {
                'IP': '127.0.0.1',
                'Gateway': '127.0.0.1'
            }

        raise RuntimeError('Not implemented exception')
