import requests
import asyncio
import aiohttp
from pprint import pprint
import datetime
from urllib3.util.url import parse_url
import pandas as pd
from lxml import html
from news_scraper.filters import *
from news_scraper.entity import *


class Scraper(object):
    def __init__(self, filter, user_agent_header, news_obj):
        self.filter = filter
        self.user_agent_header = self.user_agent_dict[user_agent_header]
        self.news_obj = news_obj
        self.news_dict = self.__get_news_dict()

    @property
    def user_agent_dict(self):
        return {'desktop': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'},

                'mobile': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) '
                                         'AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'}
                }

    def __get_news_page(self):
        response = requests.get(self.filter.url, headers=self.user_agent_header)
        if response.ok:
            return html.fromstring(response.text)
        else:
            return None

    def __get_news_items(self, root):
        items = root.xpath(self.filter.items)
        if items:
            return items
        else:
            return None

    def __get_news_dict(self):
        root = self.__get_news_page()
        items = self.__get_news_items(root)
        news_dict = {}
        if items:
            for item in items:
                topic_xpath = item.xpath(self.filter.topic)
                link_xpath = item.xpath(self.filter.link)
                source_xpath = item.xpath(self.filter.source) if self.filter.source else None
                date_xpath = item.xpath(self.filter.date) if self.filter.date else None
                news = self.news_obj(topic_xpath, link_xpath, source_xpath, date_xpath)
                news_dict[news.link] = news
        return news_dict


class ScraperLenta(Scraper):
    def __init__(self):
        super().__init__(filterLenta, 'desktop', NewsLenta)


class ScraperYandex(Scraper):
    def __init__(self):
        super().__init__(filterYandex, 'mobile', NewsYandex)


class ScraperMail(Scraper):
    def __init__(self):
        super().__init__(filterMail, 'mobile', NewsMail)
        asyncio.run(self.__get_source_date())

    async def __aioget_news_page(self, client, link):
        async with client.get(url=link) as response:
            if response.status == 200:
                txt = await response.text()
                root = html.fromstring(txt)
                source_xpath = root.xpath(self.filter.source)
                date_xpath = root.xpath(self.filter.date)
                self.news_dict[link].source = self.news_obj.get_attr(source_xpath)
                self.news_dict[link].date = self.news_obj.get_attr(date_xpath)

    async def __get_source_date(self):
        loop = asyncio.get_event_loop()
        client = aiohttp.ClientSession(loop=loop, headers=self.user_agent_header,
                                       connector=aiohttp.TCPConnector(ssl=False))
        async with client:
            await asyncio.gather(*[self.__aioget_news_page(client, link) for link in self.news_dict])



if __name__ == '__main__':
    for scraper in ScraperMail(), ScraperYandex(), ScraperLenta():
        pprint(scraper.news_dict)
