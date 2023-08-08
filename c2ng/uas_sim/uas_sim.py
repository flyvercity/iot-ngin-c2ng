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
import asyncio
import uuid
import queue

import requests
from keycloak import KeycloakOpenID
from dotenv import load_dotenv
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import tornado.websocket as ws

import common.c2ng_util as u


RECEIVE_BUFFER = 1024
'''Maximum size of the UDP receive buffer.'''

ECHO_PACKET_SIGN = b'0'
NORMAL_PACKET_SIGN = b'1'

# TODO: Get rid of globals
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
    lg.debug('KeyCloak token received')
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
        self._ws_ticket = None
        self._subscribe = False
        self._session_info = None
        self._private_key = None
        self._peer_cert_info = None
        self._peer_address = None
        self._peer_public_key = None
        self._notify_task = None

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

    def _segment(self) -> str:
        '''Get the UAS segment (ua|adx).'''
        pass

    def _peer_segment(self) -> str:
        '''Get the peer's segment (adx|ua).

        Returns:
            'adx' for the UA simulator, 'ua' for the RPS simulator.
        '''
        segment = self._segment()

        if segment == 'ua':
            return 'adx'

        return 'ua'

    def _request_session(self):
        '''Requests aerial connection from the Service.

        Returns:
            Session info JSON object.
        '''

        segment = self._segment()

        payload = {
            'ReferenceTime': datetime.now().timestamp(),
            'UasID': self._args.uasid,
            'Segment': segment
        }

        if segment == 'ua':
            payload['IMSI'] = '123456789012345'

        session_info = request(self._args, 'POST', '/session', payload)
        return session_info

    def _request_peer_certificate(self):
        '''Implements `_request_peer_certificate` for the RPS simulator.

        Returns:
            Peer's certificate info.
        '''

        segment = self._peer_segment()
        uasid = self._args.uasid
        cert_info = request(self._args, 'GET', f'/certificate/{uasid}/{segment}')
        return cert_info

    def _request_peer_address(self):
        ''' Implements `_request_peer_address` for the RPS simulator.

        Returns:
            Peer's IP address information.
        '''

        segment = self._peer_segment()
        uasid = self._args.uasid
        address_info = request(self._args, 'GET', f'/address/{uasid}/{segment}')
        return address_info

    async def _work_cycle(self):
        '''Execute internal simulation procedures. Pure virtual method.'''
        pass

    def _in_port(self) -> int:
        '''Get own UDP port.'''
        pass

    def _out_port(self) -> int:
        '''Get peer's UDP port.'''
        pass

    def _fetch_session_info(self):
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

    def _fetch_peer_address(self):
        lg.info('Requesting peer address')
        address_info = self._request_peer_address()
        lg.debug(address_info)
        self._peer_address = address_info['Address']

    def _fetch_peer_certificate(self):
        lg.info('Requesting peer certificate')
        self._peer_cert_info = self._request_peer_certificate()

        if self._args.verbose:
            u.pprint(self._peer_cert_info)

        cert = x509.load_pem_x509_certificate(
            self._peer_cert_info['Certificate'].encode()
        )

        self._peer_public_key = cert.public_key()

    async def _notify_receive_loop(self, conn):
        '''Receive loop for the notification websocket.

        Args:
            conn: websocket connection.
        '''

        while True:
            try:
                lg.info('Reading notifications')
                message = await conn.read_message()

                if not message:
                    lg.warn('Websocket closed')
                    self._subscribe = False
                    break

                payload = json.loads(message)

                lg.info('Notification received')
                u.pprint(payload)

                if payload['Action'] == 'subscribed':
                    self._subscribe = True

                if payload['Action'] == 'notification':
                    if payload['Event'] == 'peer-address-changed':
                        self._peer_address = None

                    if payload['Event'] == 'peer-credentials-changed':
                        self._peer_cert_info = None

                    if payload['Event'] == 'request-own-session':
                        self._session_info = None

            except ws.WebSocketClosedError:
                lg.warn('Websocket closed')
                self._subscribe = False
                break

            except Exception as exc:
                lg.warn(f'Error receiving notification: {exc}')
                continue

    async def _do_subscribe(self):
        segment = self._segment()
        uasid = self._args.uasid
        lg.info(f'Requesting websocket ticket for {uasid}/{segment}')
        response = request(self._args, 'POST', f'/notifications/auth/{uasid}/{segment}')
        self._ws_ticket = response['Ticket']
        lg.info('Websocket ticket received, connecting to the websocket')
        url = self._args.websocket
        conn = await ws.websocket_connect(f'{url}/notifications/websocket')

        await conn.write_message(json.dumps({
            'Ticket': self._ws_ticket,
            'Action': 'subscribe'
        }))

        lg.info('Notification subscription request sent')
        self._notify_task = asyncio.create_task(self._notify_receive_loop(conn))

        while True:
            lg.info('Waiting for notification')

            if self._subscribe:
                break

            await asyncio.sleep(1)

    async def run(self):
        '''Execute simulations.'''

        while True:
            try:
                if not self._subscribe:
                    await self._do_subscribe()

                if not self._session_info:
                    self._fetch_session_info()

                if not self._peer_address:
                    self._fetch_peer_address()

                if not self._peer_cert_info:
                    self._fetch_peer_certificate()

                await self._work_cycle()

            except KeyboardInterrupt:
                lg.info('Exiting')
                break

            except UserWarning as warn:
                lg.warn(str(warn))
                time.sleep(5)

            except Exception:
                traceback.print_exc()
                lg.info('Pause...')
                await asyncio.sleep(10)
                self._reset()

    def _secure(self):
        return True

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

    def _send_plain(self, message: bytes):
        if self._peer_address:
            self._outsocket.sendto(message, (self._peer_address, self._out_port()))

    def _send(self, message: bytes):
        packet_bytes = NORMAL_PACKET_SIGN + self._construct_sec_packet(message)
        lg.info('Transmitting')
        self._send_plain(packet_bytes)

    def _receive_plain(self):
        packet_bytes, _addr = self._insocket.recvfrom(RECEIVE_BUFFER)
        return packet_bytes

    def _receive(self) -> bytes:
        packet_bytes = self._receive_plain()
        sign = packet_bytes[0:1]

        if sign == ECHO_PACKET_SIGN:
            raise UserWarning('Unexpected packet sign (echo)')

        body_bytes = packet_bytes[1:]
        message = self._deconstruct_sec_packet(body_bytes)
        lg.info('Message received')
        return message

    def _need_reinit(self):
        if not self._subscribe:
            lg.warn('Subscription cancelled - resetting')
            return True

        if not self._session_info:
            lg.warn('Session info is missing - resetting')
            return True

        if not self._peer_address:
            lg.warn('Peer address is missing - resetting')
            return True

        if not self._peer_cert_info:
            lg.warn('Peer certificate is missing - resetting')
            return True


class SimUaC2Subsystem(SimC2Subsystem):
    '''UA C2 Subsystem Simulator.'''
    def _segment(self) -> str:
        '''Implements `_segment` for the UA simulator.

        Returns:
            'ua'.
        '''

        return 'ua'

    async def run(self):
        '''Run the simulations.

        Overrides the inherited method.
        '''

        if not self._args.signal_only:
            await super().run()
        else:
            lg.info('Starting signal reporting loop')

            while True:
                self._report_sim_signal()
                time.sleep(5)

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

    def _reset_insocket(self):
        super()._reset_insocket()
        self._insocket.settimeout(1)

    def _measure_plain_rtt(self):
        try:
            uid = str(uuid.uuid4())
            message = {'Probe': uid}
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
            u.pprint(pong_message)

            if pong_message['Probe'] != uid:
                raise UserWarning('Probe UID mismatch')
            else:
                lg.info('Probe OK')

            rtt = (pong_ts - sent_ts)/1000000  # ms
            lg.info(f'RTT: {rtt} ms')
            return rtt, False

        except TimeoutError:
            lg.warn('Probe timeout')
            return None, True

    def _measure_enc_rtt(self):
        uid = str(uuid.uuid4())
        message = {'EncryptedProbe': uid}
        u.pprint(message)
        self._send(json.dumps(message).encode())
        sent_ts = time.time_ns()

        try:
            pong_message_data = self._receive()
            pong_ts = time.time_ns()
            pong_message = json.loads(pong_message_data.decode())
            u.pprint(pong_message)

            if pong_message['EncryptedProbe'] != uid:
                raise UserWarning('Encrypted probe UID mismatch')
            else:
                lg.info('Encrypted probe OK')

            rtt = (pong_ts - sent_ts)/1000000  # ms
            lg.info(f'Encrypted RTT: {rtt} ms')

        except TimeoutError:
            lg.warn('Encrypted probe timeout')

        except InvalidSignature:
            lg.warn('Invalid peer signature - resetting peer cert')
            self._peer_cert_info = None

        except ValueError:
            lg.warn('Invalid peer public key - resetting peer cert')
            self._peer_cert_info = None

    async def _work_cycle(self):
        '''Implements `_work_cycle` for the UA simulator.'''
        lg.info('Waiting for a peer to react to notifications')
        await asyncio.sleep(2)

        while True:
            rtt, lost = self._measure_plain_rtt()
            self._measure_enc_rtt()

            if self._args.modem == 'simulated':
                self._report_sim_signal(rtt, lost)

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

        response = request(self._args, 'POST', '/signal', body={
            'ReferenceTime': datetime.now().timestamp(),
            'UasID': self._args.uasid,
            'Radio': '5G',
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
            'Baro': 100.0,
            'Heading': 35,
            'RSRP': -99 + sim_signal_flux,
            'RSRQ': -99 + sim_signal_flux,
            'RSSI': -99 + sim_signal_flux,
            'SINR': -99 + sim_signal_flux,
            'HeartbeatLoss': lost,
            'RTT': rtt
        })

        if response['Success']:
            lg.info('Signal reported')
        else:
            errors = response['Errors']
            lg.warn(f'There was an error while sending the signal: {errors}')


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
        return int(C2NG_DEFAULT_ADX_UDP_PORT)

    def _out_port(self) -> int:
        '''Implements `_out_port` for the RPS simulator.

        Returns:
            Outbound UDP port.
        '''
        return int(C2NG_DEFAULT_UA_UDP_PORT)

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
                    u.pprint(json.loads(message.decode()))
                    self._send(message)
                    lg.info('Encrypted echo packet sent back')

                except InvalidSignature:
                    lg.warn('Invalid peer signature - resetting peer cert')
                    self._peer_cert_info = None
                
                except ValueError:
                    lg.warn('Invalid peer public key - resetting peer cert')
                    self._peer_cert_info = None

            if self._need_reinit():
                break


async def run():
        '''Simulate a request on behalf of a drone.'''
        with uas_sim.SimUaC2Subsystem(self._args) as sim:
            await sim.run()

    async def adx(self):
        '''Simulate a request on behalf of a ground element (e.g., RPS).'''
        with uas_sim.SimAdxC2Subsystem(self._args) as sim:
            await sim.run()


def add_arg_subparsers(sp):
    '''Define command line arguments for this module.

    Args:
        sp: subparsers collection.
    '''

    parser.add_argument(
        '-u', '--url', help='C2NG service URL',
        default='http://localhost:9090'
    )

    parser.add_argument(
        '-w', '--websocket', help='C2NG service websocket URL',
        default='ws://localhost:9090'
    )

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

    ua.add_argument(
        '-m', '--modem', help='Modem type (none|simulated)',
        choices=['none', 'simulated'], default='none'
    )

    adx = sp.add_parser('adx', help='Command on behalf of ADX client (RPS is simulated)')
    adx.add_argument('-i', '--uasid', help='UAS Logical ID', default=C2NG_SIM_DRONE_ID)

    adx.add_argument(
        '-P', '--port', help='Incoming UDP port for RPS sim',
        type=int, default=C2NG_DEFAULT_ADX_UDP_PORT
    )
