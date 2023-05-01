#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

''' Interface with MongoDB '''

from pymongo import MongoClient


class Mongo:
    '''Mongo Client Helper '''

    def __init__(self, config):
        '''Constructor

        Args:
        - `config`: `mongo` section of the configuration dict
        '''

        self._client = MongoClient(config['uri'])

    def get_session(self, id: str) -> dict | None:
        '''Fetch a session from a collection '''
        return self._client.c2ng.c2session.find_one({'_id': id})

    def put_session(self, session: dict):
        '''Put a session object into collection '''
        session.update({'_id': session['UasID']})
        self._client.c2ng.c2session.insert_one(session)