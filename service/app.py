#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''Service Main Module'''

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

from handlers.base import HandlerBase
from handlers.sesssion import UaSessionRequestHandler, AdxSessionRequestHandler
from handlers.certificate import UaCertificateHandler, AdxCertificateHandler

DEFAULT_LISTEN_PORT = 9090


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


def handlers():
    '''Return a full set of URLSpec. '''

    return [
        (r'/test', TestHandler),
        (r'/ua/session', UaSessionRequestHandler),
        (r'/adx/session', AdxSessionRequestHandler),
        (r'/certificate/ua', UaCertificateHandler),
        (r'/certificate/adx', AdxCertificateHandler)
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
