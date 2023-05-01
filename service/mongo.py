#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

from pymongo import MongoClient


class Mongo:
    ''' Mongo Client Helper '''

    def __init__(self, config):
        ''' Constructor

        Parameters:
        - `config`: `mongo` section of the configuration dict
        '''

        self.client = MongoClient(config['uri'])

    def get_session(self, id: str):
        ''' Fetch a session from a collection '''
        return self.client.c2ng.c2session.find_one({'_id': id})

    def put_session(self, session):
        ''' Put a session object into collection '''
        session.update({'_id': session['UasID']})
        self.client.c2ng.c2session.insert_one(session)
