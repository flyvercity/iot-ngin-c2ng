#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

''' Interface with USSP Endpoint '''

import logging as lg

import requests  # TODO: asynchronize it


class UssInterface:
    def __init__(self, config) -> None:
        self.config = config

    def request(self, uasid):
        url = f"{self.config['endpoint']}/approve?UasID={uasid}"
        lg.info(f'Approving request from {uasid}')
        lg.debug(f'USS Request URL: {url}')

        try:
            answer = requests.get(url)
            answer.raise_for_status()
            response = answer.json()
            approved = response["Approved"]
            return (approved, None)

        except Exception as exc:
            lg.warn(f'USSP request failed: {exc}')
            return (None, 'Request failed')
