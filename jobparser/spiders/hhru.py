# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?L_save_area=true&clusters='
                  'true&enable_snippets=true&text=python&showClusters=true']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').extract()
        for link in vacancy:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath('//h1[@class="header"]//text()').extract_first()
        salary_min = response.xpath(('//meta[@itemprop="minValue"]/@content')).extract_first()
        salary_max = response.xpath(('//meta[@itemprop="maxValue"]/@content')).extract_first()
        salary_currency = response.xpath(('//meta[@itemprop="currency"]/@content')).extract_first()
        salary_unit = response.xpath(('//meta[@itemprop="unitText"]/@content')).extract_first()
        location = response.xpath(('//meta[@itemprop="addressLocality"]/@content')).extract_first()
        country = response.xpath(('//meta[@itemprop="addressCountry"]/@content')).extract_first()
        yield JobparserItem(url=url, name=name, salary_min=salary_min, salary_max=salary_max,
                            salary_currency=salary_currency, salary_unit=salary_unit,
                            location=location, country=country)
