# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements session handlers.'''
import logging as lg

from schemas import (
    AerialConnectionSessionRequest,
    AerialConnectionSessionResponseFailed,
    AerialConnectionSessionResponse
)

from handlers.auth import AuthHandler


class SessionHandler(AuthHandler):
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

    def post(self):
        ''' Returns new connection credentials
        ---
        summary: Request a new session for an ADX client (RPS or USS services)

        requestBody:
            description: Connectivity Session Request
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
                            AdxConnectionSessionResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            AerialConnectionSessionResponseFailed
        '''

        if not (request := self.get_request(AerialConnectionSessionRequest)):
            return

        segment = request['Segment']
        errors = {}

        if segment == 'ua':
            response, sess_errors = self.sessman.ua_session(request)

            if sess_errors:
                errors.update(sess_errors)

            if 'IMSI' not in request:
                errors['Request'] = 'imsi_required'

            if not errors:
                self.respond(AerialConnectionSessionResponse, response)
        else:
            response, errors = self.sessman.adx_session(request)

            if not errors:
                self.respond(AdxConnectionSessionResponse, response)

        if errors:
            self.fail(
                AerialConnectionSessionResponseFailed,
                errors=errors
            )
