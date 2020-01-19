# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from jobparser.filters import filter_hhru


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = filter_hhru.allowed_domains
    start_urls = filter_hhru.start_urls

    def parse(self, response: HtmlResponse):
        next_page = response.css(filter_hhru.next_page).extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.xpath(filter_hhru.vacancy).extract()
        for link in vacancy:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath(filter_hhru.name).extract_first()
        salary_min = response.xpath(filter_hhru.salary_min).extract_first()
        salary_max = response.xpath(filter_hhru.salary_max).extract_first()
        salary_currency = response.xpath(filter_hhru.salary_currency).extract_first()
        salary_unit = response.xpath(filter_hhru.salary_unit).extract_first()
        location = response.xpath(filter_hhru.location).extract_first()
        country = response.xpath(filter_hhru.country).extract_first()
        yield JobparserItem(url=url, name=name, salary_min=salary_min, salary_max=salary_max,
                            salary_currency=salary_currency, salary_unit=salary_unit,
                            location=location, country=country)
