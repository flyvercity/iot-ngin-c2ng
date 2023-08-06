# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI Tools to manage the Service and simulators.'''
import os
import logging as lg
from argparse import ArgumentParser
import queue
import asyncio

from dotenv import load_dotenv

import uas_sim
import oath_admin as oath_admin


class Handler:
    '''Command dispatcher.'''

    def __init__(self, args):
        self._args = args

    async def handle(self):
        '''Dispatch a CLI command.'''

        try:
            func = getattr(self, self._args.command)
            await func()

        except UserWarning as exc:
            print(f'Command failed: {exc}')

    async def ua(self):
        '''Simulate a request on behalf of a drone.'''
        with uas_sim.SimUaC2Subsystem(self._args) as sim:
            await sim.run()

    async def adx(self):
        '''Simulate a request on behalf of a ground element (e.g., RPS).'''
        with uas_sim.SimAdxC2Subsystem(self._args) as sim:
            await sim.run()

    async def keycloak(self):
        '''Configure the KeyCloak service.'''
        oath_admin.configure_oauth(self._args)


def setup_logging(args):
    '''Setup realtime logging parameters.

    Args:
        args: CLI parameters.
    '''

    # Setup realtime logging
    log_que = queue.Queue(-1)
    queue_handler = lg.handlers.QueueHandler(log_que)
    log_handler = lg.StreamHandler()
    queue_listener = lg.handlers.QueueListener(log_que, log_handler)
    queue_listener.start()

    lg.basicConfig(
        level=lg.DEBUG if args.verbose else lg.INFO,
        format="%(asctime)s  %(message)s", handlers=[queue_handler]
    )


async def main():
    '''C2NG CLI Tool entry point.'''
    load_dotenv()
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    parser.add_argument(
        '-u', '--url', help='C2NG service URL',
        default='http://localhost:9090'
    )

    parser.add_argument(
        '-w', '--websocket', help='C2NG service websocket URL',
        default='ws://localhost:9090'
    )

    parser.add_argument(
        '-a', '--auth', help='Address of the OIDC server (by default, KeyCloak)',
        default='http://localhost:8080/'
    )

    parser.add_argument(
        '-p', '--password', help='UA/ADX OIDC Authentication password',
        default=os.getenv('C2NG_UA_DEFAULT_PASSWORD')
    )

    sp = parser.add_subparsers(dest='command', required=True, metavar='CMD')
    uas_sim.add_arg_subparsers(sp)
    oath_admin.add_arg_subparsers(sp)
    args = parser.parse_args()
    setup_logging(args)
    await Handler(args).handle()


if __name__ == '__main__':
    asyncio.run(main())
