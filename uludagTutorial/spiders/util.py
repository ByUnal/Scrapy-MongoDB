from pymongo import MongoClient

mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["uludagCrawler"]
ulu_db = db["uludag-data"]
