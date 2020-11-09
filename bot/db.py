from pymongo import MongoClient


class MongoDBManger(object):

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.piazza
        self.collection = self.db.post

    def insert_update(self, query, new_values):
        """
        update a certain document in the posts collection

        :param query: query to get the document we want to update
        :param new_values: dict of the new value we want to set in the document
        :return: NA
        """
        params = {"$set": new_values}
        result = self.collection.update_one(query, params, upsert=True)
        if result.matched_count != 1:
            print("match not found in db")

    def insert(self, value):
        self.collection.insert_one(value)

    def find(self, query):
        """

        :param query: query to get the document for the certain post
        :return: BSON result object
        """
        return self.collection.find_one(query)

    def get_all(self):
        """
        get all document in the post collection
        :return: BSON result objects
        """
        return self.collection.find()

    def del_by_cid(self, cid):
        """

        :param cid: cid of the document to delete
        :return: BSON result object
        """
        return self.collection.delete_one({"cid": cid})

