from pprint import pprint
import ssl
import pymongo
from pymongo.errors import DuplicateKeyError
from news_scraper.passwords import MONGO_PASS


connection_str = f'mongodb+srv://KirillKras:{MONGO_PASS}' + \
                 '@testcluster-hcpdp.mongodb.net/test?retryWrites=true&w=majority'


class MongoClient(object):
    def __init__(self, index_id, db_name, collection_name, conn_str=connection_str):
        self._client = pymongo.MongoClient(conn_str, ssl_cert_reqs=ssl.CERT_NONE)
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]
        self._set_index(index_id)

    def _set_index(self, index_id):
        if f'{index_id}_1' not in self._collection.index_information():
            self._collection.create_index([(index_id, pymongo.ASCENDING)], unique=True)

    def find_all(self):
        return self._collection.find()

    def insert_one(self, row):
        self._collection.insert_one(row)

    def insert_many(self, info_dict):
        for row in info_dict.values():
            try:
                pprint(row.to_dict())
                self.insert_one(row.to_dict())
                print('Добавлено')
            except DuplicateKeyError:
                print('Дубль - не добавлено')