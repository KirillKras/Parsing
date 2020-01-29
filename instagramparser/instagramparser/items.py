# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


class InstagramparserItem(scrapy.Item):
    user = scrapy.Field()
    followers = scrapy.Field()

class InstagramPhotoItem(scrapy.Item):
    image_urls = scrapy.Field(input_processor=MapCompose())
    images = scrapy.Field()
    follower_name = scrapy.Field(output_processor=TakeFirst())