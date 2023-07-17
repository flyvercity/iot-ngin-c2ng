# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements session handlers.'''
import logging as lg

from schemas import (
    AerialConnectionSessionRequest,
    AerialConnectionSessionResponseFailed,
    AerialConnectionSessionResponse,
    AdxConnectionSessionRequest,
    AdxConnectionSessionResponse
)

from handlers.auth import AuthHandler


class SessionHandlerBase(AuthHandler):
    def delete(self, uasid):
        '''Terminates a session.

        Args:
            uasid: Logical UAS identifier

        ---
        summary: Request a new session for an ADX client (RPS or USS services)

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for the session
        responses:
            200:
                description: Success payload containing session information
                content:
                    application/json:
                        schema:
                            BaseSuccessSchema
        '''

        lg.warn(f'Session removal for {uasid}')
        # TODO: implement
        self.respond()


class UaSessionRequestHandler(SessionHandlerBase):
    '''UA Session Endpoint Handler.'''

    def post(self):
        ''' Returns new connection credentials
        ---
        summary: Request a new session for UA

        requestBody:
            description: Aerial Connectivity Session Request
            required: True
            content:
                application/json:
                    schema:
                        AerialConnectionSessionRequest

        responses:
            200:
                description: Success payload containing session information
                content:
                    application/json:
                        schema:
                            AerialConnectionSessionResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            AerialConnectionSessionResponseFailed
        '''

        if not (request := self.get_request(AerialConnectionSessionRequest)):
            return

        response, errors = self.sessman.ua_session(request)

        if errors:
            self.fail(
                AerialConnectionSessionResponseFailed,
                errors=errors
            )
        else:
            self.respond(AerialConnectionSessionResponse, response)


class AdxSessionRequestHandler(SessionHandlerBase):
    '''Aviation Data Exchange Network Session Endpoint Handler'''

    def post(self):
        ''' Returns new connection credentials
        ---
        summary: Request a new session for an ADX client (RPS or USS services)

        requestBody:
            description: ADX Connectivity Session Request
            required: True
            content:
                application/json:
                    schema:
                        AdxConnectionSessionRequest

        responses:
            200:
                description: Success payload containing session information
                content:
                    application/json:
                        schema:
                            AdxConnectionSessionResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            AdxConnectionSessionResponseFailed
        '''

        if not (request := self.get_request(AdxConnectionSessionRequest)):
            return

        uasid = request['UasID']
        response, errors = self.sessman.adx_session(uasid)

        if errors:
            self.fail(
                AerialConnectionSessionResponseFailed,
                errors=errors
            )
        else:
            self.respond(AdxConnectionSessionResponse, response)
