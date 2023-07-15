# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements certificate requests.'''
import logging as lg
import json

import tornado.websocket as ws


class WebSocketHandler(ws.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message: bytes):
        payload = json.loads(message.decode())

        if self.settings['logging']['verbose']:
            lg.debug('Incoming message websocket message')
            msg_dump = json.dumps(payload, indent=2)
            print(msg_dump)

    def on_close(self):
        pass
