#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

''' Service Main Module '''

import os
import logging as lg
import json
import yaml
import asyncio
from pathlib import Path

import tornado.web as web
from marshmallow.exceptions import ValidationError

from schemas import (
    ValidationErrorSchema,
    AerialConnectionSessionRequest,
    AerialConnectionSessionResponseFailed
)

from uss import UssInterface
from mongo import Mongo
from nsacf import NSACF


DEFAULT_LISTEN_PORT = 9090


class HandlerBase(web.RequestHandler):
    ''' Helper methods for request and errors handling '''

    def prepare(self):
        '''Creates shortcuts to subservices'''
        self.uss = self.settings['uss']  # type: UssInterface
        self.mongo = self.settings['mongo']  # type: Mongo
        self.nsacf = self.settings['nsacf']  # type: NSACF

    def _return(self, ResponseSchema: type, response: dict):
        '''Validate and return a response

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

    def respond(self, ResponseSchema: type, data: dict = {}):
        '''Successful response with optional data

        Args:
        - `ResponseSchema` - a schema of the successful response, subclass of `BaseSuccessSchema`
        - data: JSON-formattable response
        '''

        self.set_status(200)
        data['Success'] = True
        self._return(ResponseSchema, data)

    def fail(self, ResponseSchema: type, errors: dict, message: str = None):
        '''Graceful failure response

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
        ''' Exception response '''
        self.set_header('Content-Type', 'application/json')

        self.finish(json.dumps({
            'Success': False,
            'Code': status_code,
            'Errors': 'Internal Server Error'
        }))

    def get_request(self, RequestSchema):
        ''' Unmarshal and validate a JSON request

        Parameters:
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
    ''' Test Endpoint Handler '''

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


class UavSessionRequestHandler(HandlerBase):
    ''' UAV Session Endpoint Handler '''

    def post(self):
        ''' Returns new connection credentials
        ---
        summary: Request a new session for UAV

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

        session = {
            'UasID': uasid,
            "GatewayIP": '127.0.0.1',
            "UasIP": '127.0.0.1',
            "RpsIP": '127.0.0.1',
            "UavPublicKey": 'w43frgojerpgojerpvjervp',
            "UavPrivateKey": 'cdssvsdvsdvsdvsdvdsvdv'
        }

        self.mongo.put_session(session)
        self.respond()


def handlers():
    ''' Return a full set of URLSpec '''

    return [
        (r'/test', TestHandler),
        (r'/uav/session', UavSessionRequestHandler)
    ]


async def main():
    ''' Asynchronious entry point. '''
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

    app = web.Application(
        handlers(),
        config=config,
        mongo=mongo,
        uss=uss,
        nsacf=nsacf
    )

    lg.info(f'C2NG :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
