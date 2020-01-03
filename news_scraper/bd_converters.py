from pprint import pprint
import ssl
import pymongo
from pymongo.errors import DuplicateKeyError
from news_scraper.passwords import MONGO_PASS


connection_str = f'mongodb+srv://KirillKras:{MONGO_PASS}' + \
                 '@testcluster-hcpdp.mongodb.net/test?retryWrites=true&w=majority'


class NewsMongoClient(object):
    def __init__(self, connection_str=connection_str):
        self.__client = pymongo.MongoClient(connection_str, ssl_cert_reqs=ssl.CERT_NONE)
        self.__db = self.__client.NewsScraper
        self.__collection = self.__db.newsCollection
        self.__set_index()

    def __set_index(self):
        if 'link_1' not in self.__collection.index_information():
            self.__collection.create_index([('link', pymongo.ASCENDING)], unique=True)

    def find_all(self):
        return self.__collection.find()


    def insert_one(self, news):
        self.__collection.insert_one(news)

    def insert_many(self, news_dict):
        for news in news_dict.values():
            try:
                pprint(news.to_dict())
                self.insert_one(news.to_dict())
                print('Добавлено')
            except DuplicateKeyError:
                print('Дубль - не добавлено')
