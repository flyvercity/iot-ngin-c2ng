# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module integrates UA and ADX simulators and provides the entrypoint.'''

import os
import logging as lg
import asyncio

import c2ng.common.c2ng_util as u
from c2ng.uas_sim.sim_ua import SimUaC2Subsystem
from c2ng.uas_sim.sim_adx import SimAdxC2Subsystem


async def main():
    C2NG_SIM_SUBSYSTEM = os.getenv('C2NG_SIM_SUBSYSTEM')
    C2NG_SIM_DRONE_ID = os.getenv('C2NG_SIM_DRONE_ID')
    C2NG_DEFAULT_UA_UDP_PORT = os.getenv('C2NG_DEFAULT_UA_UDP_PORT')
    C2NG_DEFAULT_ADX_UDP_PORT = os.getenv('C2NG_DEFAULT_ADX_UDP_PORT')
    C2NG_UA_DEFAULT_PASSWORD = os.getenv('C2NG_UA_DEFAULT_PASSWORD')
    C2NG_SIM_VERBOSE = os.getenv('C2NG_SIM_VERBOSE')
    C2NG_SIM_OAUTH_URL = os.getenv('C2NG_SIM_OAUTH_URL')
    C2NG_SIM_CORE_URL = os.getenv('C2NG_SIM_CORE_URL')
    C2NG_SIM_CORE_WS_URL = os.getenv('C2NG_SIM_CORE_WS_URL')
    C2NG_SIM_UA_MODEM = os.getenv('C2NG_SIM_UA_MODEM')
    C2NG_SIM_USE_DID = os.getenv('C2NG_SIM_USE_DID')

    config = {
        'auth': C2NG_SIM_OAUTH_URL,
        'uasid': C2NG_SIM_DRONE_ID,
        'password': C2NG_UA_DEFAULT_PASSWORD,
        'verbose': C2NG_SIM_VERBOSE == 'true',
        'url': C2NG_SIM_CORE_URL,
        'websocket': C2NG_SIM_CORE_WS_URL,
        'ua_port': int(C2NG_DEFAULT_UA_UDP_PORT),
        'adx_port': int(C2NG_DEFAULT_ADX_UDP_PORT),
        'subsystem': C2NG_SIM_SUBSYSTEM,
        'modem': C2NG_SIM_UA_MODEM,
        'did': C2NG_SIM_USE_DID == 'true'
    }

    u.setup_logging(config['verbose'])

    lg.info('------ Starting ------')

    if config['subsystem'] == 'ua':
        lg.info('Selected UA subsystem')
        Sim = SimUaC2Subsystem
    elif config['subsystem'] == 'adx':
        lg.info('Selected ADX subsystem')
        Sim = SimAdxC2Subsystem
    else:
        raise UserWarning('Unknown subsystem')

    with Sim(config) as sim:
        await sim.run()


if __name__ == '__main__':
    asyncio.run(main())
