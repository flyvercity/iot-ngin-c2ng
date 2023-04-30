from pymongo import MongoClient


class Mongo:
    def __init__(self, config):
        self.client = MongoClient(config['uri'])

    def get_session(self, id: str):
        ''' Fetch a session from a collection '''
        return self.client.c2ng.c2session.find_one({'_id': id})

    def put_session(self, session):
        session.update({'_id': session['UasID']})
        self.client.c2ng.c2session.insert_one(session)
