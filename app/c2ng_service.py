import os
import logging as lg
import json
import asyncio
from typing import Tuple, List, Type

import tornado.web as web

DEFAULT_LISTEN_PORT = 9090

ERROR_INTERNAL_ERROR = 1


class HandlerBase(web.RequestHandler):
    ''' Helper methods for request and errors handling '''

    def respond(self, data={}):
        ''' Successful response with optional data '''
        self.set_header('Content-Type', 'application/json')
        data['Success'] = True
        self.finish(json.dumps(data) + '\n')

    def fail(self, error_id, error_str):
        ''' Graceful failure response '''
        self.set_header('Content-Type', 'application/json')
        self.set_status(400, error_str)

        self.finish(json.dumps({
            'Success': False,
            'ErrorID': error_id,
            'ErrorString': error_str
        }))

    def write_error(self, status_code, **kwargs):
        ''' Exception response '''
        self.set_header('Content-Type', 'application/json')

        self.finish(json.dumps({
            'Code': status_code,
            'Success': False,
            'ErrorID': ERROR_INTERNAL_ERROR,
            'ErrorString': 'Internal Server Error'
        }))


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
                            type: object
                            properties:
                                Success:
                                    type: boolean
        '''

        self.respond()


class UavSessionRequestHandler(HandlerBase):
    ''' UAV Session Endpoint Handler '''

    def post(self):
        ''' Returns new connection credentials
        ---
        summary: Aerial Connectivity Session Request for UAV
        '''

        self.respond()


def handlers() -> List[Tuple[str, Type[HandlerBase]]]:
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
