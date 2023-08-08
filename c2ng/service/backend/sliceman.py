# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements an interface with Network Slice Admission Control Function.'''

from c2ng.service.backend.net_providers.simulated import SimulatedSlice
from c2ng.service.backend.net_providers.cucumore import CucumoreManager


PROVIDERS = {
    'simulated': SimulatedSlice,
    'cucumore': CucumoreManager
}


class SliceMan:
    '''SliceMan API Implementation.'''

    def __init__(self, config: dict):
        '''Constructor.

        Args:
            config: contains `sliceman` section of the configuration file.

        Raises:
            RuntimeError: if provider type is not implemented.
        '''

        self._config = config
        provider_type = config.get('provider')

        if provider_type not in PROVIDERS:
            raise RuntimeError(f'Invalid provider type: {provider_type}')

        self._provider = PROVIDERS[provider_type](config[provider_type])

    async def establish(self):
        '''Perform pre-start activities of a network provider if any.'''
        await self._provider.establish()

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
        '''

        return self._provider.get_ue_network_creds(imsi)

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
            RuntimeError: if SliceMan endpoint is not implemented

        '''

        return self._provider.get_adx_network_creds(uid)
