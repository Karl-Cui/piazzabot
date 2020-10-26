from pymongo import MongoClient


class MongoDBManger(object):

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.piazza
        self.collection = self.db.post

    def insert_update(self, query, new_values):
        params = {"$set": new_values}
        result = self.collection.update_one(query, params, upsert=True)
        print(result.matched_count)

    def insert(self, value):
        result = self.collection.insert_one(value)

    def find(self, query):
        return self.collection.find_one(query)
