# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI UA and RPS Simulators.'''
import os
from datetime import datetime
import time
import traceback
import logging as lg
import socket

import requests

import tool_util as u
from keycloak import KeycloakOpenID
from dotenv import load_dotenv


load_dotenv()


C2NG_SIM_DRONE_ID = os.getenv('C2NG_SIM_DRONE_ID')
C2NG_DEFAULT_UA_UDP_PORT = os.getenv('C2NG_DEFAULT_UA_UDP_PORT')
C2NG_DEFAULT_ADX_UDP_PORT = os.getenv('C2NG_DEFAULT_ADX_UDP_PORT')


def request(args, method: str, path: str, body={}, qsp={}) -> dict:
    '''Make a authenticated request to the service

    Args:
    - `args`: CLI arguments
    - `method`: HTTP method
    - `path`: relative endpoint path
    - `body`: JSON object for call payload
    - `qsp`: a dict with query string parameters
    '''

    keycloak_openid = KeycloakOpenID(
        server_url=args.auth,
        realm_name="c2ng",
        client_id="c2-access",
        client_secret_key=os.getenv('C2NG_UAS_CLIENT_SECRET')
    )

    token = keycloak_openid.token(args.uasid, args.password)
    access_token = token['access_token']
    headers = {'Authentication': f'Bearer {access_token}'}
    url = args.url + path
    r = requests.request(method=method, url=url, json=body, params=qsp, headers=headers)
    reply = r.json()

    if 'Success' not in reply:
        raise UserWarning(f'Malformed reply: {r.text}')

    if not reply['Success']:
        if 'Errors' not in reply:
            raise UserWarning(f'Malformed failure reply: {r.text}')

        errors = reply['Errors']

        if message := reply.get('Message'):
            lg.warn(f'Error message from service: {message}')

        raise UserWarning(errors)

    return reply


class SimC2Subsystem:
    '''A base class for both UA and RPS simulators.
    Implements the Context Manager protocol.
    '''

    def __init__(self, args: dict):
        '''Constructor.

        Args:
        - `args`: CLI arguments
        '''
        self._args = args
        self._session_info = None
        self._cert_info = None

    def __enter__(self):
        '''Implements context manager's 'enter' method. Binds sockets.'''
        self._outsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._insocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self

    def __exit__(self, *args):
        '''Implements context manager's 'exit' method. Closes sockets.'''
        self._outsocket.close()
        self._insocket.close()

    def _request_session(self) -> dict:
        '''Requests a session from the service. Pure virtual method.'''
        pass

    def _request_peer_certificate(self) -> dict:
        '''Requests a certifice for the from the service. Pure virtual method.'''
        pass

    def _work_cycle(self):
        '''Execute internal simulation procedures. Pure virtual method.'''
        pass

    def _in_port(self) -> int:
        '''Get own UDP port.'''
        pass

    def _out_port(self) -> int:
        '''Get peer's UDP port.'''
        pass

    def run(self):
        '''Execute simulations.'''

        while True:
            try:
                if not self._session_info:
                    lg.info('Requesting session')
                    self._session_info = self._request_session()

                    if self._args.verbose:
                        u.pprint(self._session_info)

                    ip = self._session_info['IP']
                    port = self._in_port()
                    lg.info(f'Binding to {ip}:{port}')
                    self._insocket.bind((ip, port))

                if not self._cert_info:
                    lg.info('Requesting peer certificate')
                    self._cert_info = self._request_peer_certificate()

                    if self._args.verbose:
                        u.pprint(self._cert_info)

                self._work_cycle()

            except KeyboardInterrupt:
                lg.info('Exiting')
                break

            except UserWarning as warn:
                lg.warn(str(warn))
                time.sleep(5)
                lg.info('Restarting')

            except Exception:
                traceback.print_exc()
                lg.info('Pause...')
                time.sleep(10)
                lg.info('Restarting')

    def _send(self, message):
        pass


class SimUaC2Subsystem(SimC2Subsystem):
    '''UA C2 Subsystem Simulator.'''

    def _request_session(self):
        '''Implements `_request_session` for the UA simulator.'''

        session_info = request(self._args, 'POST', '/ua/session', body={
            'ReferenceTime': datetime.now().timestamp(),
            'UasID': self._args.uasid,
            'IMSI': '123456989012345'
        })

        return session_info

    def _request_peer_certificate(self):
        '''Implements `_request_peer_certificate` for the UA simulator.'''
        cert_info = request(self._args, 'GET', f'/certificate/adx/{self._args.uasid}')
        return cert_info

    def _in_port(self) -> int:
        '''Implements `_in_port` for the UA simulator.'''
        return int(C2NG_DEFAULT_UA_UDP_PORT)

    def _out_port(self) -> int:
        '''Implements `_out_port` for the UA simulator.'''
        return int(C2NG_DEFAULT_ADX_UDP_PORT)

    def _work_cycle(self):
        '''Implements `_work_cycle` for the UA simulator.'''

        while True:
            print('sending here')
            time.sleep(1)


class SimAdxC2Subsystem(SimC2Subsystem):
    '''RPS C2 Subsystem Simulator.'''

    def _request_session(self):
        '''Implements `_request_session` for the RPS simulator.'''
        session_info = request(self._args, 'POST', '/adx/session', {
            'ReferenceTime': datetime.now().timestamp(),
            'UasID': self._args.uasid,
        })

        return session_info

    def _request_peer_certificate(self):
        '''Implements `_request_peer_certificate` for the RPS simulator.'''
        cert_info = request(self._args, 'GET', f'/certificate/ua/{self._args.uasid}')
        return cert_info

    def _in_port(self) -> int:
        '''Implements `_in_port` for the RPS simulator.'''
        return int(C2NG_DEFAULT_ADX_UDP_PORT)

    def _out_port(self) -> int:
        '''Implements `_out_port` for the RPS simulator.'''
        return int(C2NG_DEFAULT_UA_UDP_PORT)

    def _work_cycle(self):
        '''Implements `_work_cycle` for the RPS simulator.'''
        while True:
            print('sending here')
            time.sleep(1)


def add_arg_subparsers(sp):
    '''Define command line arguments for this module.

    Args:
    - `sp`: subparsers collection.
    '''

    ua = sp.add_parser('ua', help='Command on behalf of UA')
    ua.add_argument('-i', '--uasid', help='UAS Logical ID', default=C2NG_SIM_DRONE_ID)

    ua.add_argument(
        '-P', '--port', help='Incoming UDP port for UA C2 sim',
        type=int, default=C2NG_DEFAULT_UA_UDP_PORT
    )

    adx = sp.add_parser('adx', help='Command on behalf of ADX client (RPS is simulated)')
    adx.add_argument('-i', '--uasid', help='UAS Logical ID', default=C2NG_SIM_DRONE_ID)

    adx.add_argument(
        '-P', '--port', help='Incoming UDP port for RPS sim',
        type=int, default=C2NG_DEFAULT_ADX_UDP_PORT
    )
