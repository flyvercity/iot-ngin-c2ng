# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This is the main service module.'''
import os
import logging as lg
import yaml
import asyncio
from pathlib import Path

import tornado.web as web

from c2ng.service.backend.uss import UssInterface
from c2ng.service.backend.mongo import Mongo
from c2ng.service.backend.sliceman import SliceMan
from c2ng.service.backend.influx import Influx
from c2ng.service.backend.secman import SecMan
from c2ng.service.backend.sessman import SessMan
from c2ng.service.backend.statsman import StatsMan

from c2ng.service.did.issuer import DIDIssuer

from c2ng.service.handlers.auth import fetch_keycloak_public_certs
from c2ng.service.handlers.sesssion import SessionHandler
from c2ng.service.handlers.certificate import CertificateHandler
from c2ng.service.handlers.address import AddressHandler
from c2ng.service.handlers.signal import SignalStatsHandler
from c2ng.service.handlers.did import JWTIssuerHandler
from c2ng.service.handlers.did import VerifierConfigHandler

from c2ng.service.gui.dashboard import DashboardHandler

from c2ng.service.handlers.notify import (
    WebsocketTicketManager,
    WebsocketAuthHandler,
    WsNotifyHandler
)


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
        # API endpoints
        (r'/', HomepageHandler),
        (r'/session', SessionHandler),
        (r'/certificate/([^/]+)/([^/]+)', CertificateHandler),
        (r'/address/([^/]+)/([^/]+)', AddressHandler),
        (r'/signal/([^/]+)', SignalStatsHandler),
        (r'/notifications/auth/([^/]+)/([^/]+)', WebsocketAuthHandler),
        (r'/notifications/websocket', WsNotifyHandler),
        (r'/did/jwt/([^/]+)', JWTIssuerHandler),
        (r'/did/config/([^/]+)', VerifierConfigHandler),
        # GUI pages
        (r'/gui/dashboard', DashboardHandler)
    ]


async def main():
    '''Asynchronious entry point.'''
    config_file = Path(os.getenv('C2NG_CONFIG_FILE', '/app/config/c2ng/config.yaml'))
    # TODO: Validate config
    config = yaml.safe_load(config_file.read_text())
    port = config['service']['port']
    verbose = config['logging']['verbose']
    lg.basicConfig(level=lg.DEBUG if verbose else lg.INFO)
    lg.info('---------- Starting up ----------')

    lg.debug('Executing pre-start tasks')
    await fetch_keycloak_public_certs(config)

    lg.debug('Creating backend objects')
    mongo = Mongo(config['mongo'])
    uss = UssInterface(config['uss'])
    sliceman = SliceMan(config['sliceman'])
    secman = SecMan(config['security'])
    influx = Influx(config['influx'])
    sessman = SessMan(mongo, uss, sliceman, secman)
    statsman = StatsMan(influx, sessman)
    wstxman = WebsocketTicketManager()
    didissuer = DIDIssuer(config['did'])

    lg.debug('Perform pre-start activities')
    await sliceman.establish()

    app = web.Application(
        handlers(),
        config=config,
        mongo=mongo,
        uss=uss,
        sliceman=sliceman,
        secman=secman,
        influx=influx,
        sessman=sessman,
        statsman=statsman,
        wstxman=wstxman,
        didissuer=didissuer
    )

    lg.info('---------- Restarted ----------')
    lg.info(f'Listening for requests on {port}')
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
