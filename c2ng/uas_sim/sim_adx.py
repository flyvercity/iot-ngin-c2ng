# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implement a ADX (remote pilot station) C2 subsystem simulator.'''

import logging as lg
import json

from cryptography.exceptions import InvalidSignature

import c2ng.common.c2ng_util as u
from c2ng.uas_sim.sim_base import SimC2Subsystem, ECHO_PACKET_SIGN, request


class SimAdxC2Subsystem(SimC2Subsystem):
    '''RPS C2 Subsystem Simulator.'''
    def _segment(self) -> str:
        '''Implements `_segment` for the RPS simulator.

        Returns:
            'adx'.
        '''

        return 'adx'

    def _in_port(self) -> int:
        '''Implements `_in_port` for the RPS simulator.

        Returns:
            Inbound UDP port.
        '''
        return int(self._config['adx_port'])

    def _out_port(self) -> int:
        '''Implements `_out_port` for the RPS simulator.

        Returns:
            Outbound UDP port.
        '''
        return int(self._config['ua_port'])

    async def _work_cycle(self):
        '''Implements `_work_cycle` for the RPS simulator.'''

        while True:
            lg.info('Waiting for a packet')
            packet_bytes = self._receive_plain()
            sign = packet_bytes[0:1]

            if sign == ECHO_PACKET_SIGN:
                # NOTE: the echo packet is not verified here, echoing back as is
                self._send_plain(packet_bytes)
                lg.info('Echo packet sent back')
            else:
                body_bytes = packet_bytes[1:]

                try:
                    message = self._deconstruct_sec_packet(body_bytes)
                    payload = json.loads(message.decode())

                    if self._config['verbose']:
                        u.pprint(payload)

                    if self._config['did']:
                        lg.debug('Adding DID Verified Credential JWT')
                        payload['DIDJWT'] = self._did_info

                    pong_message = json.dumps(payload).encode()
                    lg.debug('Sending back encrypted echo packet')
                    self._send(pong_message)
                    lg.info('Encrypted echo packet sent back')

                    if self._config['verbose']:
                        u.pprint(payload)

                except InvalidSignature:
                    lg.warning('Invalid peer signature - resetting peer cert')
                    self._peer_cert_info = None

                except ValueError as exc:
                    lg.error(f'Invalid peer public key - resetting peer cert. Additional info: {exc}')
                    self._peer_cert_info = None

            if self._need_reinit():
                break

    def _initialize_did(self):
        lg.info('Requesting Verified Credential JWT')
        uasid = self._config['uasid']
        response = request(self._config, 'GET', f'/did/jwt/{uasid}')
        self._did_info = response['JWT']
