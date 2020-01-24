# -*- coding: utf-8 -*-
import scrapy


class InstaphotoSpider(scrapy.Spider):
    name = 'instaphoto'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    def parse(self, response):
        pass
