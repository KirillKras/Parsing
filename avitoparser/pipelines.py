# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline
import pymongo

class AvitoPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


class DatabasePipeline(object):
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        self.mongo_db = client.avito_photos

    def process_item(self, item, spider: scrapy.Spider):
        collection = self.mongo_db[spider.name]
        collection.instert_one(item)
        return item