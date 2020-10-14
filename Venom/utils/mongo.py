import os

import pymongo

cluster = pymongo.MongoClient(os.environ['VENOM_MONGO'])
db = cluster["venom"]
users = db["users"]
crawlers = db["crawlers"]


def count_mongo(collection: pymongo.collection.Collection,
                search: dict = None):
    if search is None:
        search = {}
    return collection.count_documents(search)


def insert_mongo(collection: pymongo.collection.Collection,
                 req: dict = None):
    user_id = ("_id", count_mongo(collection) + 1)
    items = [item for item in req.items()]
    items.insert(0, user_id)
    post = {k: v for k, v in items}
    collection.insert_one(post)


def delete_mongo(collection: pymongo.collection.Collection,
                 user_id: int):
    collection.delete_one({"_id": user_id})


def replace_mongo(collection: pymongo.collection.Collection,
                  user_id: int, req: dict):
    user_id = ("_id", user_id)
    items = [item for item in req.items()]
    items.insert(0, user_id)
    post = {k: v for k, v in items}
    collection.replace_one({"_id": user_id}, post)


if __name__ == '__main__':
    print([x for x in users.find({})])
