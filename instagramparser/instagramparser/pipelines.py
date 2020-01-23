# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pymongo
from pymongo.errors import DuplicateKeyError
from scrapy.pipelines.images import ImagesPipeline
import datetime


class InstagramPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            yield scrapy.Request(item['avatar'])
        except Exception as e:
            print(e)

    def item_completed(self, results, item, info):
        if results:
            return item



class MongoPipeline(object):

    #collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        for user in item['followers']:
            user: dict = user.get('node')
            user['_id'] = user['id']
            #del user['id']
            user['date'] = str(datetime.datetime.now().date())
            try:
                self.db[item['user']].insert_one(user)
            except DuplicateKeyError:
                print('Дубликат')

        return item

    def __check_index(self, collection: str, index_id: str):
        if f'{index_id}_1' not in self.db[index_id].index_information():
            self.db[index_id].create_index([(index_id, pymongo.ASCENDING)], unique=True)