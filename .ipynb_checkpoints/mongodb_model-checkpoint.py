from pymongo import MongoClient

class MongoDB:
    def __init__(self, uri, database_name, collection_name):
        """
        Initialize the MongoDB connection.
        """
        self.client = MongoClient(uri)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        """
        Insert data into the MongoDB collection.
        :param data: A dictionary or list of dictionaries to insert.
        """
        if isinstance(data, list):
            self.collection.insert_many(data)
        else:
            self.collection.insert_one(data)

    def fetch_all_data(self):
        """
        Fetch all data from the MongoDB collection.
        :return: A list of all documents in the collection.
        """
        return list(self.collection.find())

    def fetch_data_by_query(self, query):
        """
        Fetch data matching a specific query.
        :param query: A dictionary representing the MongoDB query.
        :return: A list of matching documents.
        """
        return list(self.collection.find(query))

    def close_connection(self):
        """
        Close the MongoDB connection.
        """
        self.client.close()
