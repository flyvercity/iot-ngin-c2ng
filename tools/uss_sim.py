import logging as lg
import json
import asyncio

import tornado.web as web


class ApproveHandler(web.RequestHandler):
    ''' Simulate flight approve endpoint '''

    def get(self):
        ''' Return approval '''
        self.set_header('Content-Type', 'application/json')

        data = {
            'Approved': True
        }

        self.finish(json.dumps(data) + '\n')


def handlers():
    return [
        (r'/approve', ApproveHandler),
    ]


async def start(args):
    port = args.port
    app = web.Application(handlers())
    lg.info(f'USS SIM :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


def run(args):
    asyncio.run(start(args))
