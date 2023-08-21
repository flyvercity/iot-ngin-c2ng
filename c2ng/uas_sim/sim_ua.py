# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implement a UA (airborne) C2 subsystem simulator.'''

from datetime import datetime
import time
import logging as lg
import json
from random import random
import asyncio
import uuid

from cryptography.exceptions import InvalidSignature

import c2ng.common.c2ng_util as u
from c2ng.uas_sim.sim_base import SimC2Subsystem, ECHO_PACKET_SIGN, request


class SimUaC2Subsystem(SimC2Subsystem):
    '''UA C2 Subsystem Simulator.'''
    def _segment(self) -> str:
        '''Implements `_segment` for the UA simulator.

        Returns:
            'ua'.
        '''

        return 'ua'

    def _in_port(self) -> int:
        '''Implements `_in_port` for the UA simulator.

        Returns:
            Incoming UDP Port.'''

        return int(self._config['ua_port'])

    def _out_port(self) -> int:
        '''Implements `_out_port` for the UA simulator.

        Returns:
            Outgoing UDP Port.
        '''

        return int(self._config['adx_port'])

    def _reset_insocket(self):
        super()._reset_insocket()
        self._insocket.settimeout(1)

    def _measure_plain_rtt(self):
        try:
            uid = str(uuid.uuid4())
            message = {'Probe': uid}

            if self._config['verbose']:
                u.pprint(message)

            message_data = ECHO_PACKET_SIGN + json.dumps(message).encode()
            self._send_plain(message_data)
            sent_ts = time.time_ns()
            pong_message_data = self._receive_plain()

            if pong_message_data[0:1] != ECHO_PACKET_SIGN:
                raise UserWarning('Unexpected packet sign')

            pong_body_data = pong_message_data[1:]

            pong_ts = time.time_ns()
            pong_message = json.loads(pong_body_data.decode())

            if self._config['verbose']:
                u.pprint(pong_message)

            if pong_message['Probe'] != uid:
                raise UserWarning('Probe UID mismatch')
            else:
                lg.info('Probe OK')

            rtt = (pong_ts - sent_ts)/1000000  # ms
            lg.info(f'RTT: {rtt} ms')
            return rtt, False

        except TimeoutError:
            lg.warning('Probe timeout')
            return None, True

    def _measure_enc_rtt(self):
        uid = str(uuid.uuid4())
        message = {'EncryptedProbe': uid}

        if self._config['verbose']:
            u.pprint(message)

        self._send(json.dumps(message).encode())
        sent_ts = time.time_ns()

        try:
            pong_message_data = self._receive()
            pong_ts = time.time_ns()
            pong_message = json.loads(pong_message_data.decode())

            if self._config['verbose']:
                u.pprint(pong_message)

            if pong_message['EncryptedProbe'] != uid:
                raise UserWarning('Encrypted probe UID mismatch')
            else:
                lg.info('Encrypted probe OK')

            rtt = (pong_ts - sent_ts)/1000000  # ms
            lg.info(f'Encrypted RTT: {rtt} ms')

        except TimeoutError:
            lg.warning('Encrypted probe timeout')

        except InvalidSignature:
            lg.warning('Invalid peer signature - resetting peer cert')
            self._peer_cert_info = None

        except ValueError:
            lg.warning('Invalid peer public key - resetting peer cert')
            self._peer_cert_info = None

    async def _work_cycle(self):
        '''Implements `_work_cycle` for the UA simulator.'''
        lg.info('Waiting for a peer to react to notifications')
        await asyncio.sleep(2)

        while True:
            rtt, lost = self._measure_plain_rtt()
            self._measure_enc_rtt()

            if self._config['modem'] == 'simulated':
                lg.debug('Reporting simulated signal')
                self._report_sim_signal(rtt, lost)
            else:
                lg.debug('Skipping signal reporting')

            if self._need_reinit():
                break

            await asyncio.sleep(1)

    def _report_sim_signal(self, rtt, lost):
        '''Send simulated signal characteristics to the Service.

        Args:
            rtt: round trip time in milliseconds.
            lost: heartbeat loss flag.
        '''
        sim_signal_flux = int(15*random())
        uasid = self._config['uasid']

        perf = {}

        if rtt:
            perf['RTT'] = rtt

        if lost:
            perf['heartbeat_loss'] = lost

        response = request(self._config, 'POST', f'/signal/{uasid}', body={
            'Packet': {
                'timestamp': {
                    'unix': datetime.now().timestamp(),
                },
                'signal': {
                    'radio': '5GSA',
                    'RSRP': -99 + sim_signal_flux,
                    'RSRQ': -99 + sim_signal_flux,
                    'RSSI': -99 + sim_signal_flux,
                    'SINR': -99 + sim_signal_flux,
                },
                'perf': perf
            }
        })

        if response['Success']:
            lg.info('Signal reported')
        else:
            errors = response['Errors']
            lg.warning(f'There was an error while sending the signal: {errors}')

    def _initialize_did(self):
        lg.info('Requesting Verified Credential JWT')
        uasid = self._config['uasid']
        response = request(self._config, 'GET', f'/did/jwt/{uasid}')
        self._did_info = response['JWT']
