# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements websocket-based notifications frontend.'''
import os
import logging as lg
import json
from jose import jwt, JWTError

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
        self._connections[key] = ticket
        return ticket

    def decode_ticket(self, ticket):
        client_info = jwt.decode(ticket, self._secret, algorithms=['HS256'])
        return client_info

    def deregister_user(self, uasid, segment):
        key = f'{uasid}/{segment}'
        if key in self._connections:
            del self._connections[key]


class WebsocketAuthHandler(AuthHandler):
    def post(self, uasid, segment):
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
    def on_subscribe(self, request):
        lg.debug(f'User {self.uasid}::{self.segment} subscribing to notifications')
        sessman = self.settings['sessman']
        sessman.subscribe(self.uasid, self.segment, self)
        confirmation = json.dumps({'Action': 'subscribed'})
        self.write_message(confirmation)

    def on_unsubscribe(self, request):
        lg.debug(f'Unsubscribing {self.uasid}::{self.segment}')
        sessman = self.settings['sessman']
        sessman.unsubscribe(self.uasid, self.segment, self)

    def notify(self, event):
        lg.info(f'Notifying {self.uasid}::{self.segment} with {event}')
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

    def on_message(self, message: str):
        try:
            payload = json.loads(message)

            if self.settings['config']['logging']['verbose']:
                msg_dump = json.dumps(payload, indent=2)
                lg.debug(f'Incoming message websocket message: {msg_dump}')

            ticket = payload.get('Ticket')

            if not ticket:
                raise UserWarning('Ticket field missing')

            wstxman = self.settings['wstxman']
            client_info = wstxman.decode_ticket(ticket)
            self.uasid = client_info['UasID']
            self.segment = client_info['Segment']
            action = payload.get('Action')

            if not action:
                raise UserWarning('Action field missing')

            SchemaClass = WsNotifyHandler.ACTION_SCHEMAS.get(action)
            schema = SchemaClass()

            if not schema:
                raise UserWarning(f'Unknown action: {action}')

            if ve := schema.validate(payload):
                raise UserWarning(f'Invalid payload: {ve}')

            request = schema.load(payload)
            handler = WsNotifyHandler.ACTION_HANDLERS.get(action)
            handler(self, request)

        except JWTError as exc:
            lg.warn(f'Bad JWT token: {exc}')

            self.write_message(json.dumps({
                'Action': 'error',
                'Error': 'access_denied',
                'Message': str(exc)
            }))

        except UserWarning as exc:
            lg.warn(f'Bad websocket message: {exc}')

            self.write_message(json.dumps({
                'Action': 'error',
                'Error': 'bad_request',
                'Message': str(exc)
            }))

        except Exception as exc:
            lg.warn(f'Error processing websocket message: {exc}')
            self.close(1011, 'Internal error')

    def on_close(self):
        wstxman = self.settings['wstxman']
        wstxman.deregister_user(self.uasid, self.segment)
        sessman = self.settings['sessman']
        sessman.unsubscribe(self.uasid, self.segment)
