# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements interface with MongoDB.'''
from pymongo import MongoClient


class Mongo:
    '''Mongo client helper class.'''

    def __init__(self, config):
        '''Constructor.

        Args:
        - `config`: `mongo` section of the configuration dict
        '''

        self._client = MongoClient(config['uri'])

    def get_session(self, sid: str) -> dict | None:
        '''Fetch a session from a collection.'''
        return self._client.c2ng.c2session.find_one({'_id': sid})

    def put_session(self, session: dict):
        '''Put a session object into collection.'''
        sid = session['UasID']
        session.update({'_id': sid})

        self._client.c2ng.c2session.replace_one(
            {'_id': sid},
            session,
            upsert=True
        )
