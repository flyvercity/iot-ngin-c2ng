# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements simulated network slice control.'''


class SimulatedSlice:
    def __init__(self, config: dict):
        '''Constructor.

        Args:
            config: contains `simulated` subsection of the configuration file.
        '''

        self._config = config

    async def establish(self):
        '''Nothing to do here.'''
        pass

    def get_ue_network_creds(self, imsi: str):
        '''Get next network credentials for a UE.

        Args:
            imsi: unique UE identifier.

        Returns:
                {
                    "IP": "<address>",
                    "Gateway": "<address>"
                }
        '''

        return {
            'IP': self._config['ue'],
            'Gateway': self._config['gateway']
        }

    def get_adx_network_creds(self, uid: str):
        '''Get next network credentials for an ADX client.

        Args:
            uid: unique ID

        Returns:
                {
                    "IP": "<address>",
                    "Gateway": "<address>"
                }
        '''

        return {
            'IP': self._config['adx'],
            'Gateway': self._config['gateway']
        }
