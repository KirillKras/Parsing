# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from jobparser.filters import filter_sprjob


class SprjobSpider(scrapy.Spider):
    name = 'sprjob'
    allowed_domains = filter_sprjob.allowed_domains
    start_urls = filter_sprjob.start_urls

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(filter_sprjob.next_page).extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.xpath(filter_sprjob.vacancy).extract()
        for link in vacancy:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath(filter_sprjob.name).extract_first()
        salary_min = response.xpath(filter_sprjob.salary_min).extract_first()
        salary_max = response.xpath(filter_sprjob.salary_max).extract_first()
        if salary_max:
            salary_currency = response.xpath(filter_sprjob.salary_currency_max_with).extract_first()
        else:
            salary_currency = response.xpath(filter_sprjob.salary_currency_max_without).extract_first()
        location = response.xpath(filter_sprjob.location).extract_first()
        salary_unit = 'MONTH'
        country = ''
        yield JobparserItem(url=url, name=name, salary_min=salary_min, salary_max=salary_max,
                            salary_currency=salary_currency, salary_unit=salary_unit,
                            location=location, country=country)