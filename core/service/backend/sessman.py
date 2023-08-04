# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines Session Manager.

Session manager is the main component of the Service, which manages existing connection between UA and ADX users.
'''

import logging as lg
from base64 import b64decode as decode, b64encode as encode


class SessMan:
    def __init__(self, mongo, uss, sliceman, secman):
        self.mongo = mongo
        self.uss = uss
        self.sliceman = sliceman
        self.secman = secman
        self.subscribers = {}

    def notify(self, uasid, segment, event):
        sub_id = f'{uasid}::{segment}'

        if subscription := self.subscribers.get(sub_id):
            subscription.notify(event)

    def subscribe(self, uasid, segment, subscriber):
        self.subscribers[f'{uasid}::{segment}'] = subscriber

    def unsubscribe(self, uasid, segment):
        if f'{uasid}::{segment}' in self.subscribers:
            del self.subscribers[f'{uasid}::{segment}']

    def ua_session(self, request):
        uasid = request['UasID']
        approved, error = self.uss.request(uasid)

        if error:
            return (
                None,
                {
                    'USS': 'provider_unavailable',
                }
            )

        lg.info(f'USS approval for {uasid}: {approved}')

        if not approved:
            return (
                None,
                {
                    'USS': 'flight_not_approved'
                }
            )

        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Initializing new session for {uasid}')
            session = {'UasID': uasid}
        else:
            lg.info(f'The session exists for {uasid}')

        if 'UaCertificate' not in session:
            ua_creds = self.sliceman.get_ue_network_creds(request['IMSI'])
            session['UaIP'] = ua_creds['IP']
            session['UaGatewayIP'] = ua_creds['Gateway']
            sec_creds = self.secman.gen_client_credentials(f'{uasid}::UA')
            session['UaCertificate'] = sec_creds.cert()
            # TODO: Introduce the Key ID
            session['UaKeyID'] = encode(sec_creds.key().encode()).decode()
            self.mongo.put_session(session)
            self.notify(uasid, 'adx', 'peer-credentials-changed')
        else:
            lg.info(f'The UA endpoint established for {uasid}')

        return (
            {
                'IP': session['UaIP'],
                'GatewayIP': session['UaGatewayIP'],
                'EncryptedPrivateKey': decode(session['UaKeyID']).decode()
            },
            None
        )

    def adx_session(self, uasid):
        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Initializing new session (ADX) for {uasid}')
            session = {'UasID': uasid}
        else:
            lg.info(f'The session exist for {uasid}')

        if 'AdxCertificate' not in session:
            adx_cred = self.sliceman.get_adx_network_creds(uasid)
            session['AdxIP'] = adx_cred['IP']
            session['AdxGatewayIP'] = adx_cred['Gateway']
            sec_creds = self.secman.gen_client_credentials(f'{uasid}::ADX')
            session['AdxCertificate'] = sec_creds.cert()
            # TODO: Introduce the Key ID
            session['AdxKeyID'] = encode(sec_creds.key().encode()).decode()
            self.mongo.put_session(session)
            self.notify(uasid, 'ua', 'peer-credentials-changed')
        else:
            lg.info(f'The ADX endpoint established for {uasid}')

        return (
            {
                'IP': session['AdxIP'],
                'GatewayIP': session['AdxGatewayIP'],
                'EncryptedPrivateKey': decode(session['AdxKeyID']).decode()
            },
            None
        )
