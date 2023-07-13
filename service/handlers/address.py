# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements peer address requests.'''
import logging as lg

from schemas import (
    AddressRequestResponse,
    AddressRequestResponseFailed
)

from handlers.auth import AuthHandler


class AddressHandlerBase(AuthHandler):
    '''Peer Address Request Endpoints Handler'''

    def _address_field(self) -> str:
        '''Abstract method, an override shall return a field in the Session Mongo Object.

        Raises:
            RuntimeError: always (must be overriden).
        '''

        raise RuntimeError('This method shall be overriden.')

    def get(self, uasid):
        '''Returns an IP address for a peer.

        Args:
            uasid: Logical UAS identifier

        ---
        summary: Request a current address from existing connectivity session.

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to fetch the peer's address.

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

        address = session.get(self._address_field())

        if not address:
            self.fail(AddressRequestResponseFailed, {
                'Session': 'peer_not_connected'
            })

            return

        self.respond(AddressRequestResponse, {
            'Address': address
        })


class UaAddressHandler(AddressHandlerBase):
    '''UA Address Request Base Endpoints Handler'''

    def _address_field(self) -> str:
        '''Virtual method override.

        Returns:
            "UaIP"
        '''

        return 'UaIP'


class AdxAddressHandler(AddressHandlerBase):
    '''ADX Address Request Base Endpoints Handler'''

    def _address_field(self) -> str:
        '''Virtual method override.

        Returns:
            "AdxIP"
        '''

        return 'AdxIP'
