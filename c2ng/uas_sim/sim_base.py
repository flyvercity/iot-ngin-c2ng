# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implement a generic C2 subsystem simulator.'''

import os
from datetime import datetime
import time
import traceback
import logging as lg
import socket
import base64
import json
import asyncio

import requests
from keycloak import KeycloakOpenID
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import tornado.websocket as ws

import c2ng.common.c2ng_util as u


RECEIVE_BUFFER = 1024
'''Maximum size of the UDP receive buffer.'''

ECHO_PACKET_SIGN = b'0'
'''Binary signature of the echo (plaintext) packet.'''

NORMAL_PACKET_SIGN = b'1'
'''Binary signature of the normal (encrypted) packet.'''


def request(config, method: str, path: str, body={}, qsp={}) -> dict:
    '''Make a authenticated request to the service.

    Args:
        config: configuration dict.
        method: HTTP method.
        path: relative endpoint path.
        body: JSON object for call payload.
        qsp: a dict with query string parameters.

    Returns:
        Response as a JSON object.

    Raises:
        UserWarning: when server's response is malformed.
    '''

    secret = os.getenv('C2NG_UAS_CLIENT_SECRET')

    keycloak_openid = KeycloakOpenID(
        server_url=config['auth'],
        realm_name="c2ng",
        client_id="c2-access",
        client_secret_key=secret
    )

    token = keycloak_openid.token(config['uasid'], config['password'])
    lg.debug('KeyCloak token received')
    access_token = token['access_token']
    headers = {'Authentication': f'Bearer {access_token}'}
    url = config['url'] + path
    r = requests.request(method=method, url=url, json=body, params=qsp, headers=headers)
    reply = r.json()

    if 'Success' not in reply:
        raise UserWarning(f'Malformed reply: {r.text}')

    if not reply['Success']:
        if 'Errors' not in reply:
            raise UserWarning(f'Malformed failure reply: {r.text}')

        errors = reply['Errors']

        if message := reply.get('Message'):
            lg.warning(f'Error message from service: {message}')

        raise UserWarning(errors)

    return reply


class SimC2Subsystem:
    '''A base class for both UA and RPS simulators.

    Implements the Context Manager protocol.
    '''

    def __init__(self, config: dict):
        '''Constructor.

        Args:
            config: configuration dict.
        '''

        self._config = config
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
        self._did_info = None

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
            'UasID': self._config['uasid'],
            'Segment': segment
        }

        if segment == 'ua':
            payload['IMSI'] = '123456789012345'

        session_info = request(self._config, 'POST', '/session', payload)
        return session_info

    def _request_peer_certificate(self):
        '''Implements `_request_peer_certificate` for the RPS simulator.

        Returns:
            Peer's certificate info.
        '''

        segment = self._peer_segment()
        uasid = self._config['uasid']
        cert_info = request(self._config, 'GET', f'/certificate/{uasid}/{segment}')
        return cert_info

    def _request_peer_address(self):
        ''' Implements `_request_peer_address` for the RPS simulator.

        Returns:
            Peer's IP address information.
        '''

        segment = self._peer_segment()
        uasid = self._config['uasid']
        address_info = request(self._config, 'GET', f'/address/{uasid}/{segment}')
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

        if self._config['verbose']:
            u.pprint(self._session_info)

        ip = self._session_info['IP']
        port = self._in_port()
        lg.debug(f'Binding to {ip}:{port}')
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

        if self._config['verbose']:
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
                    lg.warning('Websocket closed')
                    self._subscribe = False
                    break

                payload = json.loads(message)

                lg.info('Notification received')

                if self._config['verbose']:
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
                lg.warning('Websocket closed')
                self._subscribe = False
                break

            except Exception as exc:
                lg.warning(f'Error receiving notification: {exc}')
                continue

    async def _do_subscribe(self):
        lg.info('Subscribing to notifications')
        segment = self._segment()
        uasid = self._config['uasid']
        lg.debug(f'Requesting websocket ticket for {uasid}/{segment}')
        response = request(self._config, 'POST', f'/notifications/auth/{uasid}/{segment}')
        self._ws_ticket = response['Ticket']
        lg.debug('Websocket ticket received, connecting to the websocket')
        url = self._config['websocket']
        conn = await ws.websocket_connect(f'{url}/notifications/websocket')

        await conn.write_message(json.dumps({
            'Ticket': self._ws_ticket,
            'Action': 'subscribe'
        }))

        lg.debug('Notification subscription request sent')
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

                if self._config['did'] and not self._did_info:
                    self._initialize_did()

                await self._work_cycle()

            except KeyboardInterrupt:
                lg.info('Exiting')
                break

            except UserWarning as warn:
                lg.warning(str(warn))
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
            addr = (self._peer_address, self._out_port())
            self._outsocket.sendto(message, addr)
            lg.debug(f'UDP packet sent to {addr}')

    def _send(self, message: bytes):
        packet_bytes = NORMAL_PACKET_SIGN + self._construct_sec_packet(message)
        lg.debug('Transmitting')
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
        lg.debug('Message received')
        return message

    def _need_reinit(self):
        if not self._subscribe:
            lg.warning('Subscription cancelled - resetting')
            return True

        if not self._session_info:
            lg.warning('Session info is missing - resetting')
            return True

        if not self._peer_address:
            lg.warning('Peer address is missing - resetting')
            return True

        if not self._peer_cert_info:
            lg.warning('Peer certificate is missing - resetting')
            return True
