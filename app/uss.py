import logging as lg

import requests  # TODO: asynchronize it


class UssInteface:
    def __init__(self, config) -> None:
        self.config = config

    def request(self, request):
        uavid = request['uavid']
        url = f"{self.config['uss']['endpoint']}/approve?UavID={uavid}"
        lg.info(f'Approving request from {uavid}')
        lg.info(f'USS Request URL: {url}')
        answer = requests.get(url)
        answer.raise_for_status()
        response = answer.json()
        approved = {response["Approved"]}
        lg.info(f'Result for {uavid}: {approved}')
        return approved
