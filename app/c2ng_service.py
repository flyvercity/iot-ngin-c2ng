import os
import logging as lg
import json
import asyncio
import traceback

import tornado.web as web


DEFAULT_LISTEN_PORT = 9090

ERROR_SUCCESS=0
ERROR_INTERNAL_ERROR = 1


class HandlerBase(web.RequestHandler):
    def respond(self, data={}):
        self.set_header('Content-Type', 'application/json')
        data['Success'] = True
        self.finish(json.dumps(data) + '\n')

    def fail(self, error_id, error_str):
        self.set_header('Content-Type', 'application/json')
        self.set_status(400, error_str)

        self.finish(json.dumps({
            'Success': False,
            'ErrorID': error_id,
            'ErrorString': error_str
        }))

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')

        self.finish(json.dumps({
            'Code': status_code,
            'Success': False,
            'ErrorID': ERROR_INTERNAL_ERROR,
            'ErrorString': 'Internal Server Error'
        }))


class MainHandler(HandlerBase):
    def get(self):
        self.respond()


def handlers():
    return [
        (r'/', MainHandler)
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
