#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''Interface with Network Slice Admission Control Function'''


class NSACF:
    '''NSACF API'''

    def __init__(self, config: dict):
        '''Constructor.

        Parameters:
        - `config` - `nsacf` section of the configuration file
        '''

        self._config = config

    def get_ue_network_creds(self, imsi: str):
        '''Get next network credentials for a UE.

        Parameters:
        - `imsi` - unique UE identified

        Returns:

        ```json
            {
                "IP": "<address>",
                "Gateway": "<address>"
            }
        ```
        '''

        if self._config.get('simulated'):
            return {
                'IP': '127.0.0.1',
                'Gateway': '127.0.0.1'
            }

        raise RuntimeError('Not implemented exception')

    def get_ground_network_creds(self, uid):
        '''Get next network credentials for an ADX client.

        Parameters:
        - `uid` - uniqie client identifier

        Returns:

        ```json
            {
                "IP": "<address>",
                "Gateway": "<address>"
            }
        ```
        '''

        if self._config.get('simulated'):
            return {
                'IP': '127.0.0.1',
                'Gateway': '127.0.0.1'
            }

        raise RuntimeError('Not implemented exception')
