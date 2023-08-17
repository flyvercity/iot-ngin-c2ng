# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines Session Manager.

Session manager is the main component of the Service, which manages existing connection between UA and ADX users.
'''

import logging as lg


class SessMan:
    def __init__(self, mongo, uss, sliceman, secman):
        self.mongo = mongo
        self.uss = uss
        self.sliceman = sliceman
        self.secman = secman
        self.subscribers = {}

    def _sub_id(self, uasid, segment):
        return f'{uasid}::{segment}'

    def notify(self, uasid, segment, event):
        sub_id = self._sub_id(uasid, segment)

        if subscription := self.subscribers.get(sub_id):
            lg.info(f'SessMan :: Notifying {sub_id} about {event}')

            subscription.notify({
                'Action': 'notification',
                'Event': event
            })

        else:
            lg.info(f'SessMan :: No subscriber for {sub_id}')

    def subscribe(self, uasid, segment, subscriber):
        sub_id = self._sub_id(uasid, segment)
        lg.info(f'SessMan :: Subscribing {sub_id}')
        self.subscribers[sub_id] = subscriber

    def unsubscribe(self, uasid, segment):
        sub_id = self._sub_id(uasid, segment)

        if sub_id in self.subscribers:
            lg.info(f'SessMan :: Unsubscribing {sub_id}')
            del self.subscribers[sub_id]
        else:
            lg.info(f'SessMan :: No subscriber to unsubscribe for {sub_id}')

    def ua_session(self, request):
        uasid = request['UasID']

        if 'IMSI' not in request:
            return (
                None,
                {
                    'Request': 'imsi_required'
                }
            )

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

        lg.info(f'Generating credentials for {uasid} - UA')
        ua_creds = self.sliceman.get_ue_network_creds(request['IMSI'])
        sec_creds = self.secman.gen_client_credentials(f'{uasid}::UA')

        session['UA'] = {
            'IP': ua_creds['IP'],
            'GatewayIP': ua_creds['Gateway'],
            'KID': sec_creds.kid(),
            'Certificate': sec_creds.cert()
        }

        self.mongo.put_session(session)
        self.notify(uasid, 'adx', 'peer-address-changed')
        self.notify(uasid, 'adx', 'peer-credentials-changed')

        return (
            {
                'IP': session['UA']['IP'],
                'GatewayIP': session['UA']['GatewayIP'],
                'KID': session['UA']['KID'],
                'EncryptedPrivateKey': sec_creds.key()
            },
            None
        )

    def adx_session(self, request):
        uasid = request['UasID']

        if not (session := self.mongo.get_session(uasid)):
            lg.info(f'Initializing new session (ADX) for {uasid}')
            session = {'UasID': uasid}
        else:
            lg.info(f'The session exist for {uasid}')

        lg.info(f'Generating credentials for {uasid} - ADX')
        adx_cred = self.sliceman.get_adx_network_creds(uasid)
        sec_creds = self.secman.gen_client_credentials(f'{uasid}::ADX')

        session['ADX'] = {
            'IP': adx_cred['IP'],
            'GatewayIP': adx_cred['Gateway'],
            'KID': sec_creds.kid(),
            'Certificate': sec_creds.cert()
        }

        self.mongo.put_session(session)
        self.notify(uasid, 'ua', 'peer-address-changed')
        self.notify(uasid, 'ua', 'peer-credentials-changed')

        return (
            {
                'IP': session['ADX']['IP'],
                'GatewayIP': session['ADX']['GatewayIP'],
                'KID': session['ADX']['KID'],
                'EncryptedPrivateKey': sec_creds.key()
            },
            None
        )
