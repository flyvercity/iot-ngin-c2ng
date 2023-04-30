import os
import logging as lg
import json
import yaml
import asyncio
from pathlib import Path

import tornado.web as web
from marshmallow.exceptions import ValidationError

from schemas import ValidationErrorSchema
from schemas import AerialConnectionSessionRequest, AerialConnectionSessionResponseFailed
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


def with_request(RequestSchema):
    def decorator(func):
        def wrapper(object):
            try:
                payload = json.loads(object.request.body)
                schema = RequestSchema()
                schema.validate(payload)
                request = schema.load(payload)
                return func(object, request)

            except ValidationError as ve:
                object.fail(ValidationErrorSchema, ve.messages_dict)

        return wrapper

    return decorator


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

    @with_request(AerialConnectionSessionRequest)
    def post(self, request):
        ''' Returns new connection credentials
        ---
        summary: Aerial Connectivity Session Request for UAV
        '''
        uss = self.settings['uss']

        try:
            approved = not uss.request(request)

            if not approved:
                self.fail(AerialConnectionSessionResponseFailed, {
                    'USS': 'Denied'
                })
            else:
                self.respond()
        except Exception:
            self.fail(AerialConnectionSessionResponseFailed, {
                'USS': 'Request failed'
            })


def handlers():
    return [
        (r'/test', TestHandler),
        (r'/uav/session', UavSessionRequestHandler)
    ]


async def main():
    config_file = Path(os.getenv('C2NG_CONFIG_FILE', '/etc/c2ng/config.yaml'))
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
