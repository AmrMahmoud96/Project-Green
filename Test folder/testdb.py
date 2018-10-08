from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db=client.test
db.object.insert({"code":"nothing"})
for a in db.object.find():
    print(a)
