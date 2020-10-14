import os

import pymongo

cluster = pymongo.MongoClient(os.environ['VENOM_MONGO'])
db = cluster["venom"]
users = db["users"]
crawlers = db["crawlers"]


class MongoConnection:

    def __init__(self):
        client = pymongo.MongoClient(os.environ['VENOM_MONGO'])
        self.db = client["venom"]

    def get_collection(self, name):
        self.collection = self.db[name]


class Users(MongoConnection):
    def __init__(self):
        super(Users, self).__init__()
        self.get_collection('users')

    def update_and_save(self, data, *fields):
        if self.collection.find(
                {'username': data['username']}
        ).count():
            for field in fields:
                self.collection.update(
                    {'username': data['username']},
                    {'$set': {field: data[field]}})

    def add(self, data):
        if not self.collection.find(
                {'username': data['username'],
                 'crawler': data['crawler']}
        ).count():
            self.collection.insert_one(data)

    def remove(self, data, *fields):
        if 'username' in fields:
            raise AttributeError(
                "You cannot delete a user"
            )
        for field in fields:
            self.collection.update(
                {'username': data['username']},
                {'$unset': {field: data[field]}}
            )


class Crawlers(MongoConnection):
    def __init__(self):
        super(Crawlers, self).__init__()
        self.get_collection('crawlers')

    def update_and_save(self, data, *fields):
        if not self.collection.find(
                {'username': data['username'],
                 'crawler': data['crawler']}
        ).count():
            for field in fields:
                self.collection.update(
                    {'username': data['username']},
                    {'$set': {field: data[field]}})

    def add(self, data):
        if not self.collection.find(
                {'username': data['username'],
                 'crawler': data['crawler']}
        ).count():
            self.collection.insert_one(data)

    def remove(self, data, remove_crawler=False, *fields):
        if remove_crawler:
            self.collection.remove(
                {'username': data['username'],
                 'crawler': data['crawler']}
            )
        for field in fields:
            self.collection.update(
                {'username': data['username']},
                {'$unset': {field: data[field]}})
