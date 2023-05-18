#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''Service Main Module'''
import logging as lg

from schemas import (
    CertificateRequestResponse,
    CertificateRequestResponseFailed
)

from handlers.auth import AuthHandler


class CertificateHandlerBase(AuthHandler):
    '''Peer Certificate Request Base Endpoints Handler'''

    def _certificate_field(self) -> str:
        '''Abstract method, an override shall return a field in the Session Mongo Object'''
        raise RuntimeError('This method shall be overriden')

    def get(self, uasid):
        ''' Returns new connection credentials
        ---
        summary: Request a new session for an ADX client (RPS or USS services)

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to fetch the peer's certificate

        responses:
            200:
                description: Success payload containing peer's certificate
                content:
                    application/json:
                        schema:
                            CertificateRequestResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            CertificateRequestResponseFailed
        '''

        if not uasid:
            self.fail(CertificateRequestResponseFailed, {
                'UasID': 'not_found'
            })

            return

        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Session not found for {uasid}')
            self.fail(CertificateRequestResponseFailed, {
                'Session': 'session_not_found'
            })

            return

        cert = session.get(self._certificate_field())

        if not cert:
            self.fail(CertificateRequestResponseFailed, {
                'Session': 'peer_not_connected'
            })

            return

        self.respond(CertificateRequestResponse, {
            'Certificate': cert
        })


class UaCertificateHandler(CertificateHandlerBase):
    '''UA Certificate Request Base Endpoints Handler'''

    def _certificate_field(self) -> str:
        '''Returns "UaCertificate"'''
        return 'UaCertificate'


class AdxCertificateHandler(CertificateHandlerBase):
    '''ADX Certificate Request Base Endpoints Handler'''

    def _certificate_field(self) -> str:
        '''Returns "AdxCertificate"'''
        return 'AdxCertificate'
