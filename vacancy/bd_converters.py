from pprint import pprint
import ssl
import pymongo
from pymongo.errors import DuplicateKeyError
from vacancy.passwords import MONGO_PASS


connection_str = f'mongodb+srv://KirillKras:{MONGO_PASS}' + \
                 '@testcluster-hcpdp.mongodb.net/test?retryWrites=true&w=majority'


class VacancyMongoClient(object):

    def __init__(self, connection_str=connection_str):
        self.__client = pymongo.MongoClient(connection_str, ssl_cert_reqs=ssl.CERT_NONE)
        self.__db = self.__client.parserDB
        self.__collection = self.__db.vacancyCollection
        self.__set_index()

    def __set_index(self):
        if 'link_1' not in self.__collection.index_information():
            self.__collection.create_index([('link', pymongo.ASCENDING)], unique=True)

    def find_all(self):
        return self.__collection.find()

    def find_vacancy_gt(self, compensation: float):
        assert compensation >= 0
        return self.__collection.find({'min_compensation': {'$gt': compensation}})

    def insert_one(self, vacancy):
        self.__collection.insert_one(vacancy)

    def insert_many(self, vacancy_list):
        for vacancy in vacancy_list:
            try:
                self.insert_one(vacancy)
                print('Добавлено')
            except DuplicateKeyError:
                print('Дубль - не добавлено')
                pprint(vacancy)
                pprint(self.__collection.find_one({'link': vacancy['link']}))




