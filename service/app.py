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

from uss import UssInteface


DEFAULT_LISTEN_PORT = 9090


class HandlerBase(web.RequestHandler):
    ''' Helper methods for request and errors handling '''

    def respond(self, data={}):
        ''' Successful response with optional data '''
        self.set_header('Content-Type', 'application/json')
        data['Success'] = True
        self.finish(json.dumps(data) + '\n')

    def fail(self, ResponseSchema, errors):
        ''' Graceful failure response '''
        self.set_header('Content-Type', 'application/json')
        self.set_status(400)
        response = {'Success': False, 'Errors': errors}
        schema = ResponseSchema()

        try:
            schema.validate(response)
            self.finish(json.dumps(response) + '\n')

        except ValidationError as ve:
            lg.error(f'Invalid response {response}: {ve}')
            raise RuntimeError('Invalid response')

    def write_error(self, status_code, **kwargs):
        ''' Exception response '''
        self.set_header('Content-Type', 'application/json')

        self.finish(json.dumps({
            'Success': False,
            'Code': status_code,
            'Errors': 'Internal Server Error'
        }))

    def get_request(self, RequestSchema):
        try:
            payload = json.loads(self.request.body)
            schema = RequestSchema()
            schema.validate(payload)
            request = schema.load(payload)
            return request

        except ValidationError as ve:
            object.fail(ValidationErrorSchema, ve.messages_dict)
            return None


class TestHandler(HandlerBase):
    ''' Test Endpoint Handler '''

    def get(self):
        ''' Return empty success result
        ---
        summary: Return empty success result
        responses:
            200:
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

        uss = self.settings['uss']
        approved, error = uss.request(request)

        if error:
            self.fail(AerialConnectionSessionResponseFailed, {'USS': error})
            return

        lg.info(f'USS approval for {request["uasid"]}: {approved}')
        self.respond()


def handlers():
    return [
        (r'/test', TestHandler),
        (r'/uav/session', UavSessionRequestHandler)
    ]


async def main():
    config_file = Path(os.getenv('C2NG_CONFIG_FILE', '/c2ng/config/config.yaml'))
    # TODO: Validate config
    config = yaml.safe_load(config_file.read_text())
    port = config['service']['port']
    verbose = config['logging']['verbose']
    lg.basicConfig(level=lg.DEBUG if verbose else lg.INFO)
    lg.debug('C2NG :: Starting up')
    uss = UssInteface(config)
    app = web.Application(handlers(), uss=uss, config=config)
    lg.info(f'C2NG :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
