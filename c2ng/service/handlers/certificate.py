# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements certificate requests.'''
import logging as lg

from c2ng.service.schemas import (
    CertificateRequestResponse,
    CertificateRequestResponseFailed
)

from c2ng.service.handlers.auth import AuthHandler


FIELD_DEFS = {
    'ua': 'UA',
    'adx': 'ADX'
}


class CertificateHandler(AuthHandler):
    '''Peer Certificate Request Base Endpoints Handler'''

    def get(self, uasid, segment):
        '''Returns a security certificate for a peer.

        Args:
            uasid: Logical UAS identifier
            segment: Airborne ('ua') or Ground ('adx') segment

        ---
        summary: Request a current certificate from existing connectivity session.

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to fetch the peer's certificate
            -   in: path
                name: Segment
                schema:
                    type: string
                    enum: [ua, adx]
                required: true
                description: Segment for which to fetch the peer's certificate

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

        if not (field := FIELD_DEFS.get(segment)):
            lg.warning(f'Invalid segment {uasid}:{segment}')
            self.fail(CertificateRequestResponseFailed, {
                'Segment': 'invalid'
            })

            return

        unit_session = session.get(field)
        kid = unit_session.get('KID')
        cert = unit_session.get('Certificate')

        if not cert:
            self.fail(CertificateRequestResponseFailed, {
                'Session': 'peer_not_connected'
            })

            return

        self.respond(CertificateRequestResponse, {
            'KID': kid,
            'Certificate': cert
        })
