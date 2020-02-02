# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import ssl
import datetime
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import pymongo
from pymongo.errors import DuplicateKeyError


class InstagramPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'image_urls' not in item:
            return
        for image_url in item['image_urls']:
            try:
                yield scrapy.Request(image_url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            raise DropItem("Item contains no files")
        return item



class MongoPipeline(object):

    #collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db, ssl_cert_reqs):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.ssl_cert_reqs = ssl_cert_reqs

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE',),
            ssl_cert_reqs=crawler.settings.get('SSL_CA_CERTS')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri,
                                          ssl_ca_certs=self.ssl_cert_reqs,
                                          ssl_cert_reqs=ssl.CERT_REQUIRED)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if spider.name == 'instaphoto':
            print(spider.name)
            return item
        for user in item['followers']:
            user: dict = user.get('node')
            user['_id'] = int(user['id'])
            del user['id']
            user['date'] = str(datetime.datetime.now().date())
            try:
                self.db[item['user']].insert_one(user)
                print(f'Добавлен {user["username"]} в {item["user"]}')
            except DuplicateKeyError:
                print('Дубликат')

        return item

    def __check_index(self, collection: str, index_id: str):
        if f'{index_id}_1' not in self.db[index_id].index_information():
            self.db[index_id].create_index([(index_id, pymongo.ASCENDING)], unique=True)