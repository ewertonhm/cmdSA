from pymongo import MongoClient
import pymongo


def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://cmdsa:<password>@cluster0.lf6al.mongodb.net/sa?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    return client['sa']


def drop_collection(collection_name):
    db = get_database()
    collection = db[collection_name]
    collection.drop()


def insert_one(collection_name, json):
    db = get_database()
    collection = db[collection_name]

    collection.insert_one(json)


def insert_many(collection_name, json_array):
    db = get_database()
    collection = db[collection_name]

    collection.insert_many(json_array)


def query(collection_name, query={}):
    db = get_database()
    collection = db[collection_name]

    result = collection.find(query)

    return result
