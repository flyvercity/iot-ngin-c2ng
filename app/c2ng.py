import os
import logging as lg
import json
import asyncio

import tornado.web as web


DEFAULT_LISTEN_PORT = 9090


class MainHandler(web.RequestHandler):
    def get(self):
        self.write(json.dumps({'result': 'hello-2'}) + '\n')


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
