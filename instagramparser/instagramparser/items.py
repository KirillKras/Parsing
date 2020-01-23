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

class InstagramparserPhotoItem(scrapy.Item):
    follower_name = scrapy.Field()
    avatar_hd_url = scrapy.Field()