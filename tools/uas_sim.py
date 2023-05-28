# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI UA and RPS Simulators.'''
import os
from datetime import datetime
import time
import traceback
import logging as lg
import socket
import base64
import json
from random import random

import requests
from keycloak import KeycloakOpenID
from dotenv import load_dotenv
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import tool_util as u


RECEIVE_BUFFER = 1024
'''Maximum size of the UDP receive buffer.'''

load_dotenv()

C2NG_SIM_DRONE_ID = os.getenv('C2NG_SIM_DRONE_ID')
C2NG_DEFAULT_UA_UDP_PORT = os.getenv('C2NG_DEFAULT_UA_UDP_PORT')
C2NG_DEFAULT_ADX_UDP_PORT = os.getenv('C2NG_DEFAULT_ADX_UDP_PORT')


def request(args, method: str, path: str, body={}, qsp={}) -> dict:
    '''Make a authenticated request to the service.

    Args:
        args: CLI arguments.
        method: HTTP method.
        path: relative endpoint path.
        body: JSON object for call payload.
        qsp: a dict with query string parameters.

    Returns:
        Response as a JSON object.

    Raises:
        UserWarning: when server's response is malformed.
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
            args: CLI arguments.
        '''

        self._args = args
        self._insocket = None
        self._outsocket = None
        self._reset()

    def _reset(self):
        lg.info('Reset')
        self._session_info = None
        self._private_key = None
        self._peer_cert_info = None
        self._peer_public_key = None

    def _reset_insocket(self):
        if self._insocket:
            self._insocket.close()
            self._insocket = None

        self._insocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __enter__(self):
        '''Implements context manager's 'enter' method. Binds sockets.

        Returns:
            Self.
        '''

        self._outsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._reset_insocket()
        return self

    def __exit__(self, *args):
        '''Implements context manager's 'exit' method. Closes sockets.

        Args:
            args: Standard argument (unused).
        '''
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
                    self._reset_insocket()
                    self._insocket.bind((ip, port))

                    # NB: using known client secret as passphase
                    client_secret = os.getenv('C2NG_UAS_CLIENT_SECRET')

                    self._private_key = load_pem_private_key(
                        self._session_info['EncryptedPrivateKey'].encode(),
                        client_secret.encode()
                    )

                if not self._peer_cert_info:
                    lg.info('Requesting peer certificate')
                    self._peer_cert_info = self._request_peer_certificate()

                    if self._args.verbose:
                        u.pprint(self._peer_cert_info)

                    cert = x509.load_pem_x509_certificate(
                        self._peer_cert_info['Certificate'].encode()
                    )

                    self._peer_public_key = cert.public_key()

                self._work_cycle()

            except KeyboardInterrupt:
                lg.info('Exiting')
                break

            except UserWarning as warn:
                lg.warn(str(warn))
                time.sleep(5)

            except Exception:
                traceback.print_exc()
                lg.info('Pause...')
                time.sleep(10)
                self._reset()

    def _secure(self):
        return False

    def _construct_sec_packet(self, message: bytes):
        lg.info('Encrypting and signing the packet')

        if not self._secure():
            return message

        encrypted = self._peer_public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        signature = self._private_key.sign(
            encrypted,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        packet = {
            'Message': base64.b64encode(encrypted).decode(),
            'Signature': base64.b64encode(signature).decode()
        }

        return json.dumps(packet).encode()

    def _deconstruct_sec_packet(self, packet_bytes) -> bytes:
        lg.info('Verifying and decrypting the packet')

        if not self._secure():
            return packet_bytes

        packet = json.loads(packet_bytes.decode())
        encrypted = base64.b64decode(packet['Message'])
        signature = base64.b64decode(packet['Signature'])

        self._peer_public_key.verify(
            signature, encrypted,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        message = self._private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return message

    def _send(self, message: bytes, address: tuple):
        packet_bytes = self._construct_sec_packet(message)
        lg.info('Transmitting')
        self._outsocket.sendto(packet_bytes, address)

    def _receive(self):
        lg.info('Receiving')
        packet_bytes, addr = self._insocket.recvfrom(RECEIVE_BUFFER)
        message = self._deconstruct_sec_packet(packet_bytes)
        return (message, addr)


class SimUaC2Subsystem(SimC2Subsystem):
    '''UA C2 Subsystem Simulator.'''

    def run(self):
        '''Run the simulations.

        Overrides the inherited method.
        '''

        if not self._args.signal_only:
            super().run()

        while True:
            lg.info('Staring signal reporting loop')
            self._report_sim_signal()
            time.sleep(5)

    def _request_session(self):
        '''Implements `_request_session` for the UA simulator.

        Returns:
            Session info object:
            * ReferenceTime (str)
            * UasID (str)
            * IMSI (str)
        '''

        session_info = request(self._args, 'POST', '/ua/session', body={
            'ReferenceTime': datetime.now().timestamp(),
            'UasID': self._args.uasid,
            'IMSI': '123456989012345'
        })

        return session_info

    def _request_peer_certificate(self):
        '''Implements `_request_peer_certificate` for the UA simulator.

        Returns:
            Peer's security certificate.
        '''

        cert_info = request(self._args, 'GET', f'/certificate/adx/{self._args.uasid}')
        return cert_info

    def _in_port(self) -> int:
        '''Implements `_in_port` for the UA simulator.

        Returns:
            Incoming UDP Port.'''

        return int(C2NG_DEFAULT_UA_UDP_PORT)

    def _out_port(self) -> int:
        '''Implements `_out_port` for the UA simulator.

        Returns:
            Outgoing UDP Port.
        '''

        return int(C2NG_DEFAULT_ADX_UDP_PORT)

    def _work_cycle(self):
        '''Implements `_work_cycle` for the UA simulator.'''
        counter = 0

        while True:
            message = f'Heartbeat #{counter}'
            print('MESSAGE:', message)
            counter += 1
            self._send(message.encode(), ('127.0.0.1', self._out_port()))
            self._report_sim_signal()
            time.sleep(1)

    def _report_sim_signal(self):
        '''Send simulated signal characteristics to the Service.'''
        sim_signal_flux = int(15*random())

        response = request(self._args, 'POST', '/signal', body={
            'ReferenceTime': datetime.now().timestamp(),
            'UasID': self._args.uasid,
            'Radio': '5gnr',
            'Cell': '1234567890',
            'Waypoint': {
                'Latitude': 35.0,
                'Longitude': 35.0,
                'Altitude': 100.0
            },
            'Roll': 0,
            'Pitch': 0,
            'Yaw': 0,
            'VNorth': 0.0,
            'VEast': 0.0,
            'VDown': 0.0,
            'VAir': 10.0,
            'Baro': 100.0 + 5.0*random(),
            'Heading': 35 + random(),
            'RSRP': -99 + sim_signal_flux,
            'RSRQ': -99 + sim_signal_flux,
            'RSSI': -99 + sim_signal_flux,
            'SINR': -99 + sim_signal_flux,
            'HeartbeatLoss': (random() < 0.01),
            'RTT': 50 + int(10*random())
        })

        u.pprint(response)


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
            message, _addr = self._receive()
            print('MESSAGE:', message.decode())


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

    ua.add_argument(
        '-S', '--signal-only', help='Do not connect, transmit signal only',
        action='store_true', default=False
    )

    adx = sp.add_parser('adx', help='Command on behalf of ADX client (RPS is simulated)')
    adx.add_argument('-i', '--uasid', help='UAS Logical ID', default=C2NG_SIM_DRONE_ID)

    adx.add_argument(
        '-P', '--port', help='Incoming UDP port for RPS sim',
        type=int, default=C2NG_DEFAULT_ADX_UDP_PORT
    )
