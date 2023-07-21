# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements peer address requests.'''
import logging as lg

from schemas import (
    AddressRequestResponse,
    AddressRequestResponseFailed
)

from handlers.auth import AuthHandler


FIELD_DEFS = {
    'ua': 'UaIP',
    'adx': 'AdxIP'
}


class AddressHandler(AuthHandler):
    '''Peer Address Request Endpoints Handler'''

    def get(self, uasid, segment):
        '''Returns an IP address for a peer.

        Args:
            uasid: Logical UAS identifier
            segment: Airborne ('ua') or Ground ('adx') segment

        ---
        summary: Request a current address from existing connectivity session.

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to fetch the peer's address.
            -   in: path
                name: Segment
                schema:
                    type: string
                    enum: [ua, adx]
                required: true
                description: Segment for which to fetch the peer's certificate

        responses:
            200:
                description: Success payload containing peer's address
                content:
                    application/json:
                        schema:
                            AddressRequestResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            AddressRequestResponseFailed
        '''

        if not uasid:
            self.fail(AddressRequestResponseFailed, {
                'UasID': 'not_found'
            })

            return

        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Session not found for {uasid}')
            self.fail(AddressRequestResponseFailed, {
                'Session': 'session_not_found'
            })

            return

        if not (field := FIELD_DEFS.get(segment)):
            lg.warn(f'Invalid segment {uasid}:{segment}')
            self.fail(AddressRequestResponseFailed, {
                'Segment': 'invalid'
            })

            return

        address = session.get(field)

        if not address:
            self.fail(AddressRequestResponseFailed, {
                'Session': 'peer_not_connected'
            })

            return

        self.respond(AddressRequestResponse, {
            'Address': address
        })
