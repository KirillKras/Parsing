# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from avitoparser.items import AvitoparserItem
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = []

    def __init__(self, section: str):
        super(AvitoSpider, self).__init__()
        self.start_urls = [f'https://www.avito.ru/rossiya/{section}', ]

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//a[@class="snippet-link"]/@href')
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=AvitoparserItem(), response=response)
        loader.add_xpath('name', '//span[@class="title-info-title-text"]/text()')
        loader.add_xpath('photos', '//div[contains(@class, "gallery-img-frame")]/@data-url')
        yield loader.load_item()

        # name = response.xpath('//span[@class="title-info-title-text"]/text()').extract_first()
        # photos = response.xpath('//div[contains(@class, "gallery-img-frame")]/@data-url').extract()
        # yield AvitoparserItem(name=name, photos=photos)