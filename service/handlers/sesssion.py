# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements session handlers.'''
import logging as lg

from schemas import (
    AerialConnectionSessionRequest,
    AerialConnectionSessionResponseFailed,
    AerialConnectionSessionResponse,
    AdxConnectionSessionRequest,
    AdxConnectionSessionResponse,
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
        '''

        lg.warn(f'Session removal for {uasid}')


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

        uasid = request['UasID']
        approved, error = self.uss.request(uasid)

        if error:
            self.fail(AerialConnectionSessionResponseFailed, {
                    'USS': 'provider_unavailable',
                },
                message=error
            )

            return

        lg.info(f'USS approval for {uasid}: {approved}')

        if not approved:
            self.fail(AerialConnectionSessionResponseFailed, {
                'USS': 'flight_not_approved'
            })

            return

        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Initializing new session for {uasid}')
            session = {'UasID': uasid}
        else:
            lg.info(f'The session exist for {uasid}')

        if 'UaCertificate' not in session:
            ua_creds = self.nsacf.get_ue_network_creds(request['IMSI'])
            session['UaIP'] = ua_creds['IP']
            session['UaGatewayIP'] = ua_creds['Gateway']
            sec_creds = self.secman.gen_client_credentials(f'{uasid}::UA')
            session['UaCertificate'] = sec_creds.cert()
            # TODO: Introduce the Key ID
            session['UaKeyID'] = sec_creds.key()
            self.mongo.put_session(session)
        else:
            lg.info(f'The UA endpoint established for {uasid}')

        response = {
            'IP': session['UaIP'],
            'GatewayIP': session['UaGatewayIP'],
            'EncryptedPrivateKey': session['UaKeyID']
        }

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

        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Initializing new session (ADX) for {uasid}')
            session = {'UasID': uasid}
        else:
            lg.info(f'The session exist for {uasid}')

        if 'AdxCertificate' not in session:
            adx_cred = self.nsacf.get_adx_network_creds(uasid)
            session['AdxIP'] = adx_cred['IP']
            session['AdxGatewayIP'] = adx_cred['Gateway']
            sec_creds = self.secman.gen_client_credentials(f'{uasid}::ADX')
            session['AdxCertificate'] = sec_creds.cert()
            # TODO: Introduce the Key ID
            session['AdxKeyID'] = sec_creds.key()
            self.mongo.put_session(session)
        else:
            lg.info(f'The ADX endpoint established for {uasid}')

        response = {
            'IP': session['AdxIP'],
            'GatewayIP': session['AdxGatewayIP'],
            'EncryptedPrivateKey': session['AdxKeyID']
        }

        self.respond(AdxConnectionSessionResponse, response)
