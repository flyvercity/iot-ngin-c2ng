# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements interface with MongoDB.'''
import logging as lg

from pymongo import MongoClient


class Mongo:
    '''Mongo client helper class.'''

    def __init__(self, config):
        '''Constructor.

        Args:
            config: `mongo` section of the configuration dict
        '''

        uri = config['uri']
        lg.info(f'Connecting to MongoDB on {uri}')
        self._client = MongoClient(uri)

    def get_session(self, sid: str) -> dict | None:
        '''Fetch a session from a collection.

        Args:
            sid: session identifier.

        Returns:
            A session JSON object.
        '''
        return self._client.c2ng.c2session.find_one({'_id': sid})

    def put_session(self, session: dict):
        '''Put a session object into collection.

        Args:
            session: a session JSON object.
        '''
        sid = session['UasID']
        session.update({'_id': sid})

        self._client.c2ng.c2session.replace_one(
            {'_id': sid},
            session,
            upsert=True
        )
