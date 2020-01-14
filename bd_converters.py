from pprint import pprint
import ssl
import pymongo
from pymongo.errors import DuplicateKeyError
from news_scraper.passwords import MONGO_PASS


connection_str = f'mongodb+srv://KirillKras:{MONGO_PASS}' + \
                 '@testcluster-hcpdp.mongodb.net/test?retryWrites=true&w=majority'


class MongoClient(object):
    def __init__(self, index_id, db_name, collection_name, conn_str=connection_str):
        self.__client = pymongo.MongoClient(conn_str, ssl_cert_reqs=ssl.CERT_NONE)
        self.__db = self.__client[db_name]
        self.__collection = self.__db[collection_name]
        self.__set_index(index_id)

    def __set_index(self, index_id):
        if f'{index_id}_1' not in self.__collection.index_information():
            self.__collection.create_index([(index_id, pymongo.ASCENDING)], unique=True)

    def find_all(self):
        return self.__collection.find()

    def insert_one(self, row):
        self.__collection.insert_one(row)

    def insert_many(self, info_dict):
        for row in info_dict.values():
            try:
                pprint(row.to_dict())
                self.insert_one(row.to_dict())
                print('Добавлено')
            except DuplicateKeyError:
                print('Дубль - не добавлено')