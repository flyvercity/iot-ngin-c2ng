# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements websocket-based notifications frontend.'''
import os
import logging as lg
import json
from jose import jwt

import tornado.websocket as ws

from schemas import (
    WsAuthResponseSuccess,
    WsAuthResponseFailed,
    AsyncSubscribeSchema,
    AsyncUnsubscribeSchema
)


from handlers.auth import AuthHandler


class WebsocketTicketManager:
    def __init__(self):
        self._secret = os.getenv('C2NG_WS_AUTH_SECRET')

        if not self._secret:
            raise RuntimeError('C2NG_WS_AUTH_SECRET not set')

        self._connections = {}

    def register_user(self, uasid, segment):
        key = f'{uasid}/{segment}'

        client_info = {
            'UasID': uasid,
            'Segment': segment
        }

        ticket = jwt.encode(client_info, self._secret, algorithm='HS256')
        self.connections[key] = ticket
        return ticket

    def decode_ticket(self, ticket):
        client_info = jwt.decode(ticket, self._secret, algorithms=['HS256'])
        return client_info

    def deregister_user(self, uasid, segment):
        key = f'{uasid}/{segment}'
        if key in self.connections:
            del self.connections[key]


class WebsocketAuthHandler(AuthHandler):
    def get(self, uasid, segment):
        errors = {}

        if not uasid:
            errors['UasID'] = 'not_found'

        if not segment:
            errors['Segment'] = 'not_found'
        elif segment not in ['ua', 'adx']:
            errors['Segment'] = 'bad_segment'

        if errors:
            self.fail(WsAuthResponseFailed, errors)
            return

        wstxman = self.settings['wstxman']
        ticket = wstxman.register_user(uasid, segment)

        self.respond(WsAuthResponseSuccess, {
            'Ticket': ticket
        })


class WsNotifyHandler(ws.WebSocketHandler):
    def on_subscribe(self):
        sessman = self.settings['sessman']
        sessman.subscribe(self.uasid, self.segment, self)
        confirmation = json.dumps({'Action': 'subscribed'})
        self.write_message(confirmation)

    def on_unsubscribe(self):
        sessman = self.settings['sessman']
        sessman.unsubscribe(self.uasid, self.segment, self)

    def notify(self, event):
        self.write_message(json.dumps(event))

    ACTION_SCHEMAS = {
        'subscribe': AsyncSubscribeSchema,
        'unsubscribe': AsyncUnsubscribeSchema
    }

    ACTION_HANDLERS = {
        'subscribe': on_subscribe,
        'unsubscribe': on_unsubscribe
    }

    def open(self):
        self.uasid = None
        self.segment = None

    def on_message(self, message: bytes):
        payload = json.loads(message.decode())

        if self.settings['logging']['verbose']:
            lg.debug('Incoming message websocket message')
            msg_dump = json.dumps(payload, indent=2)
            print(msg_dump)

        payload = json.loads(self.request.body)

        ticket = payload.get('Ticket')

        if not ticket:
            raise ws.WebSocketError('Ticket field missing')

        wsctxman = self.settings['wsctxman']
        client_info = wsctxman.decode_ticket(ticket)
        self.uasid = client_info['UasID']
        self.segment = client_info['Segment']
        action = payload.get('Action')

        if not action:
            raise ws.WebSocketError('Action field missing')

        schema = WsNotifyHandler.ACTION_SCHEMAS.get(action)

        if not schema:
            raise ws.WebSocketError(f'Unknown action: {action}')

        if ve := schema.validate(payload):
            raise ws.WebSocketError(f'Invalid payload: {ve}')

        request = schema.load(payload)
        handler = WsNotifyHandler.ACTION_HANDLERS.get(action)
        handler(self, request)

    def on_close(self):
        wsctxman = self.settings['wsctxman']
        wsctxman.deregister_user(self.uasid, self.segment)
        sessman = self.settings['sessman']
        sessman.unsubscribe(self.uasid, self.segment, self)
