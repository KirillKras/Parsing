from dataclasses import dataclass
from typing import List

@dataclass
class Filter:
    allowed_domains: List[str]
    start_urls: List[str]
    next_page: str
    vacancy: str
    name: str
    salary_min: str
    salary_max: str
    location: str


@dataclass
class FilterHH(Filter):
    salary_currency: str
    salary_unit: str
    country: str


@dataclass
class FilterSJ(Filter):
    salary_currency_max_with: str
    salary_currency_max_without: str


filter_hhru = FilterHH(
    allowed_domains=['hh.ru',],
    start_urls=['https://hh.ru/search/vacancy?L_save_area=true&clusters='
                  'true&enable_snippets=true&text=python&showClusters=true',],
    next_page='a.HH-Pager-Controls-Next::attr(href)',
    vacancy='//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    name='//h1[@class="header"]//text()',
    salary_min='//meta[@itemprop="minValue"]/@content',
    salary_max='//meta[@itemprop="maxValue"]/@content',
    salary_currency='//meta[@itemprop="currency"]/@content',
    salary_unit='//meta[@itemprop="unitText"]/@content',
    location='//meta[@itemprop="addressLocality"]/@content',
    country='//meta[@itemprop="addressCountry"]/@content'
)

filter_sprjob = FilterSJ(
    allowed_domains=['superjob.ru', ],
    start_urls=['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bc%5D%5B0%5D=1', ],
    next_page='//a[contains(@class, "f-test-button-dalshe")]/@href',
    vacancy='//a[contains(@class, "icMQ_ _1QIBo")]/@href',
    name='//h1[@class="_3mfro rFbjy s1nFK _2JVkc"]//text()',
    salary_min='//span[@class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"]//span[1]//text()',
    salary_max='//span[@class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"]//span[3]//text()',
salary_currency_max_with='//span[@class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"]//span[4]//text()',
    salary_currency_max_without='//span[@class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"]//span[2]//text()',
    location='//span[@class="_6-z9f"]//text()',
)
