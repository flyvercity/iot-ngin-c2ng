# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import logging as lg

from c2ng.service.handlers.auth import AuthHandler

from c2ng.service.schemas import (
    DIDJWTRequestResponse,
    DIDJWTRequestResponseFailed,
    DIDConfigRequestResponse,
    DIDConfigRequestResponseFailed
)


class JWTIssuerHandler(AuthHandler):
    '''DID JWT Request Base Endpoints Handler'''

    def get(self, uasid):
        '''Returns DID JWT for a given UAS.

        Args:
            uasid: Logical UAS identifier

        ---
        summary: Request a Verificable Credential in a form of signed JWT.

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to issue a Verificable Credential.

        responses:
            200:
                description: Success payload containing JWT-encoded Verificable Credential.
                content:
                    application/json:
                        schema:
                            DIDJWTRequestResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            DIDJWTRequestResponseFailed
        '''

        try:
            jwt = self.didissuer.issue_jwt(uasid)
            self.respond(DIDJWTRequestResponse, {'JWT': jwt})

        except Exception as e:
            lg.error(f'Unable to issue JWT for UAS {uasid}: {e}')
            self.fail(DIDJWTRequestResponseFailed, {'UasID': 'not_found'})


class VerifierConfigHandler(AuthHandler):
    '''DID Verifier Config Request Base Endpoints Handler'''

    def get(self, uasid):
        '''Returns configuration for a Credential Verifier.

        Args:
            uasid: Logical UAS identifier

        ---
        summary: Request a configuration for a Credential Verifier from a central authority ("issuer").

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to issue a Verificable Credential.

        responses:
            200:
                description: Success payload containing JWT-encoded Verificable Credential.
                content:
                    application/json:
                        schema:
                            DIDConfigRequestResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            DIDConfigRequestResponseFailed
        '''

        try:
            config = self.didissuer.generate_config(uasid)
            self.respond(DIDConfigRequestResponse, {'Config': config})

        except Exception as e:
            lg.error(f'Unable to issue JWT for UAS {uasid}: {e}')
            self.fail(DIDConfigRequestResponseFailed, {'UasID': 'not_found'})
