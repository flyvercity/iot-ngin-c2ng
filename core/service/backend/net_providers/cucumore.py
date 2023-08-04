# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements Cumucore network control API version 5.'''


class CucumoreManager:
    def __init__(self, config: dict):
        '''Constructor.

        Args:
            config: contains `cucumore` subsection of the configuration file.
        '''

        self._config = config

    async def establish(self):
        pass

    def get_ue_network_creds(self, imsi: str):
        pass

    def get_adx_network_creds(self, uid: str):
        pass
