#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''Service Main Module'''
import logging as lg

from schemas import (
    AerialConnectionSessionRequest,
    AerialConnectionSessionResponseFailed,
    AerialConnectionSessionResponse,
    AdxConnectionSessionRequest,
    AdxConnectionSessionResponse,
)

from handlers.auth import AuthHandler


class UaSessionRequestHandler(AuthHandler):
    '''UA Session Endpoint Handler'''

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

        ua_creds = self.nsacf.get_ue_network_creds(request['IMSI'])
        session['UaIP'] = ua_creds['IP']
        session['UaGatewayIP'] = ua_creds['Gateway']
        sec_creds = self.secman.gen_client_credentials(f'{uasid}::UA', 'secret')
        session['UaCertificate'] = sec_creds.cert()
        self.mongo.put_session(session)

        response = {
            'IP': session['UaIP'],
            'GatewayIP': session['UaGatewayIP'],
            'EncryptedPrivateKey': sec_creds.key()
        }

        self.respond(AerialConnectionSessionResponse, response)


class AdxSessionRequestHandler(AuthHandler):
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

        adx_cred = self.nsacf.get_adx_network_creds(uasid)
        session['AdxIP'] = adx_cred['IP']
        session['AdxGatewayIP'] = adx_cred['Gateway']
        sec_creds = self.secman.gen_client_credentials(f'{uasid}::ADX', 'secret')
        session['AdxCertificate'] = sec_creds.cert()
        self.mongo.put_session(session)

        response = {
            'IP': session['AdxIP'],
            'GatewayIP': session['AdxGatewayIP'],
            'EncryptedPrivateKey': sec_creds.key()
        }

        self.respond(AdxConnectionSessionResponse, response)
