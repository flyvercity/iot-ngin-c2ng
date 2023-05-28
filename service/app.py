# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This is the main service module.'''
import os
import logging as lg
import yaml
import asyncio
from pathlib import Path

import tornado.web as web


from uss import UssInterface
from mongo import Mongo
from nsacf import NSACF
from secman import SecMan
from influx import Influx

from handlers.sesssion import UaSessionRequestHandler, AdxSessionRequestHandler
from handlers.certificate import UaCertificateHandler, AdxCertificateHandler
from handlers.signal import SignalStatsHandler

DEFAULT_LISTEN_PORT = 9090


class HomepageHandler(web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/html')
        self.finish('<html><body><h1>C2NG</h1></body></html>')


def handlers():
    '''Defines the HTTP endpoints.

    Returns:
        A list of URL specifications.
    '''

    return [
        (r'/', HomepageHandler),
        (r'/ua/session', UaSessionRequestHandler),
        (r'/adx/session', AdxSessionRequestHandler),
        (r'/certificate/ua/([^/]+)', UaCertificateHandler),
        (r'/certificate/adx/([^/]+)', AdxCertificateHandler),
        (r'/signal', SignalStatsHandler)
    ]


async def main():
    '''Asynchronious entry point.'''
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
    influx = Influx(config['influx'])

    app = web.Application(
        handlers(),
        config=config,
        mongo=mongo,
        uss=uss,
        nsacf=nsacf,
        secman=secman,
        influx=influx
    )

    lg.info('---------- C2NG Restarted ----------')
    lg.info(f'C2NG :: Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
