import os
import logging as lg
import json
import asyncio

import tornado.web as web

from schemas import AerialConnectionSessionRequest


DEFAULT_LISTEN_PORT = 9090


class HandlerBase(web.RequestHandler):
    ''' Helper methods for request and errors handling '''

    def respond(self, data={}):
        ''' Successful response with optional data '''
        self.set_header('Content-Type', 'application/json')
        data['Success'] = True
        self.finish(json.dumps(data) + '\n')

    def fail(self, errors):
        ''' Graceful failure response '''
        self.set_header('Content-Type', 'application/json')
        self.set_status(400, str(errors))

        self.finish(json.dumps({
            'Success': False,
            'Errors': errors
        }))

    def write_error(self, status_code, **kwargs):
        ''' Exception response '''
        self.set_header('Content-Type', 'application/json')

        self.finish(json.dumps({
            'Code': status_code,
            'Success': False,
            'Errors': 'Internal Server Error'
        }))

    def prepare(self):
        ''' Unmarshal the payload if present '''
        if self.request.body:
            self.payload = json.loads(self.request.body)

    def get_request(self, RequestSchema):
        ''' Validate the payload agains given class '''
        request = RequestSchema()
        ve = request.validate(self.payload)

        if ve:
            self.fail(ve)

        return request.load(self.payload)


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
        summary: Aerial Connectivity Session Request for UAV
        '''
        request = self.get_request(AerialConnectionSessionRequest)
        self.respond()


def handlers():
    return [
        (r'/test', TestHandler),
        (r'/uav/session', UavSessionRequestHandler)
    ]


async def main():
    port = os.getenv('C2NG_SERVICE_PORT', DEFAULT_LISTEN_PORT)
    verbose = os.getenv('C2NG_LOGGING_VERBOSE', 0)
    lg.basicConfig(level=lg.DEBUG if verbose else lg.INFO)
    lg.debug('C2NG :: Starting up')
    app = web.Application(handlers())
    lg.info(f'C2NG :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
