import requests
from pprint import pprint
import datetime
from urllib3.util.url import parse_url
from lxml import html
from news_scraper.filters import *
from news_scraper.entity import NewsLenta


class Scraper(object):
    def __init__(self, filter, user_agent_header):
        self.filter = filter
        self.user_agent_header = self.user_agent_dict[user_agent_header]
        self.news_list = self.__get_news_list()

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

    def __get_news_list(self):
        root = self.__get_news_page()
        items = self.__get_news_items(root)
        news_list = []
        if items:
            for item in items:
                topic_xpath = item.xpath(self.filter.topic)
                link_xpath = item.xpath(self.filter.link)
                if self.filter.source:
                    source = item.xpath(self.filter.source)
                news_list.append(NewsLenta(topic_xpath, link_xpath))
        return news_list


class ScraperLenta(Scraper):
    def __init__(self):
        super().__init__(filterLenta, 'desktop')


class ScraperYandex(Scraper):
    def __init__(self):
        super().__init__(filterYandex, 'mobile')


if __name__ == '__main__':
    scraper = ScraperLenta()
    for news in scraper.news_list:
        pprint(news)