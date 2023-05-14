#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''Service Main Module'''

import os
import logging as lg
import json
import yaml
import asyncio
from pathlib import Path

import tornado.web as web
from marshmallow.exceptions import ValidationError

from schemas import (
    BaseSuccessSchema,
    ValidationErrorSchema,
    AerialConnectionSessionRequest,
    AerialConnectionSessionResponseFailed,
    AerialConnectionSessionResponse,
    AdxConnectionSessionRequest,
    AdxConnectionSessionResponse
)

from uss import UssInterface
from mongo import Mongo
from nsacf import NSACF
from secman import SecMan 


DEFAULT_LISTEN_PORT = 9090


class HandlerBase(web.RequestHandler):
    '''Helper methods for request and errors handling'''

    def prepare(self):
        '''Creates shortcuts to subservices.'''
        self.uss = self.settings['uss']  # type: UssInterface
        self.mongo = self.settings['mongo']  # type: Mongo
        self.nsacf = self.settings['nsacf']  # type: NSACF
        self.secman = self.settings['secman']  # type: SecMan

    def _return(self, ResponseSchema: type, response: dict):
        '''Validate and return a response.

        Args:
        - `ResponseSchema` - a schema of the response, subclass of `Schema`
        - `response` - a dict with formattable data
        '''

        self.set_header('Content-Type', 'application/json')
        schema = ResponseSchema()

        try:
            ve = schema.validate(response)

            if ve:
                raise ValidationError(ve)

            self.finish(json.dumps(response) + '\n')

        except ValidationError as ve:
            lg.error(f'Invalid response {response}: {ve}')
            raise RuntimeError('Invalid response')

    def respond(self, ResponseSchema: type = BaseSuccessSchema, data: dict = {}):
        '''Successful response with optional data

        Args:
        - `ResponseSchema` - a schema of the successful response, subclass of `BaseSuccessSchema`
        - data: JSON-formattable response
        '''

        self.set_status(200)
        data['Success'] = True
        self._return(ResponseSchema, data)

    def fail(self, ResponseSchema: type, errors: dict, message: str = None):
        '''Produces a graceful failure response.

        Args:
        - `ResponseSchema` - a schema of the erroneous response, subclass of `ErrorSchema`
        - `errors` - a dict with structured error
        - `message` - an optional human readable message
        '''

        self.set_status(400)
        response = {'Success': False, 'Errors': errors}

        if message:
            response.update({'Message': message})

        self._return(ResponseSchema, response)

    def write_error(self, status_code, **kwargs):
        '''Produces an exception response'''
        self.set_header('Content-Type', 'application/json')

        self.finish(json.dumps({
            'Success': False,
            'Code': status_code,
            'Errors': 'Internal Server Error'
        }))

    def get_request(self, RequestSchema):
        '''Unmarshal and validate a JSON request

        Args:
        - `RequestSchema` - a type of the request to validate against
        '''

        try:
            payload = json.loads(self.request.body)
            schema = RequestSchema()

            if ve := schema.validate(payload):
                raise ValidationError(ve)

            request = schema.load(payload)
            return request

        except ValidationError as ve:
            self.fail(ValidationErrorSchema, ve.messages_dict)
            return None


class TestHandler(HandlerBase):
    '''Test Endpoint Handler'''

    def get(self):
        ''' Return empty success result
        ---
        summary: Return empty success result
        responses:
            200:
                description: Minimum success response
                content:
                    application/json:
                        schema:
                            BaseSuccessSchema
        '''

        self.respond()


class UaSessionRequestHandler(HandlerBase):
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


class AdxSessionRequestHandler(HandlerBase):
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


def handlers():
    '''Return a full set of URLSpec. '''

    return [
        (r'/test', TestHandler),
        (r'/ua/session', UaSessionRequestHandler),
        (r'/adx/session', AdxSessionRequestHandler)
    ]


async def main():
    '''Asynchronious entry point. '''
    config_file = Path(os.getenv('C2NG_CONFIG_FILE', '/c2ng/config/config.yaml'))
    # TODO: Validate config
    config = yaml.safe_load(config_file.read_text())
    port = config['service']['port']
    verbose = config['logging']['verbose']
    lg.basicConfig(level=lg.DEBUG if verbose else lg.INFO)
    lg.debug('C2NG :: Starting up')
    mongo = Mongo(config['mongo'])
    uss = UssInterface(config['uss'])
    nsacf = NSACF(config['nsacf'])
    secman = SecMan(config['security'])

    app = web.Application(
        handlers(),
        config=config,
        mongo=mongo,
        uss=uss,
        nsacf=nsacf,
        secman=secman
    )

    lg.info(f'C2NG :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
