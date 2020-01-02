from abc import ABC, abstractmethod
from urllib3.util.url import parse_url
import datetime
import json


class News(object):
    @staticmethod
    def get_attr(attr_xpath, base_attr=None):
        if attr_xpath:
            attr = attr_xpath[0]
            attr = attr.replace('\xa0', ' ')
            return attr
        return base_attr

    def __init__(self, topic_xpath, link_xpath, source_xpath, date_xpath):
        self._topic = News.get_attr(topic_xpath)
        self._link = News.get_attr(link_xpath)
        self._link = self._get_link(self._link)
        self._source = News.get_attr(source_xpath)
        self._date = News.get_attr(date_xpath, datetime.datetime.now().date())


    def _get_link(self, link):
        parsed_link = parse_url(link)
        if parsed_link.scheme and parsed_link.hostname:
            return f'{parsed_link.scheme}://{parsed_link.hostname}{parsed_link.path}'
        elif parsed_link.hostname:
            return f'https://{parsed_link.hostname}{parsed_link.path}'
        elif parsed_link.path:
            return f'https://{self.url}{parsed_link.path}'
        else:
            return None


    @property
    def topic(self):
        return self._topic

    @property
    def link(self):
        return self._link

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        if source and type(source) == str:
            self._source = source
        else:
            self._source = self.url

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        if type(date) == datetime.datetime:
            self._date = date
        else:
            self._date = datetime.datetime.now().date()

    def to_dict(self):
        d = {
            'topic': self.topic,
            'link': self.link,
            'source': self.source,
            'date': self.date.__str__()
        }
        return d

    def __repr__(self):
        return self.to_dict().__repr__()

    def __str__(self):
        return self.__repr__()


class NewsLenta(News):
    def __init__(self, topic_xpath, link_xpath, source_xpath=None, date_xpath=None):
        self.url = 'lenta.ru'
        super().__init__(topic_xpath, link_xpath, source_xpath, date_xpath)
        if self.link:
            self._source = parse_url(self.link).hostname
            date = self.__get_date()
            if date:
                self._date = date

    def __get_date_link_lenta(self):
        link_split = self.link.split('/')
        return datetime.date(year=int(link_split[-5]),
                             month=int(link_split[-4]),
                             day=int(link_split[-3]))

    def __get_date_link_moslenta(self):
        link_split = self.link.split('-')
        return datetime.date(year=int(link_split[-1].split('.')[0]),
                             month=int(link_split[-2]),
                             day=int(link_split[-3]))

    def __get_date(self):
        parsed_link = parse_url(self.link)
        if parsed_link.hostname == self.url:
            return self.__get_date_link_lenta()
        elif parsed_link.hostname == 'moslenta.ru':
            return self.__get_date_link_moslenta()
        else:
            return None


class NewsYandex(News):
    def __init__(self, topic_xpath, link_xpath, source_xpath, date_xpath=None):
        self.url = 'yandex.ru'
        super().__init__(topic_xpath, link_xpath, source_xpath, date_xpath)


class NewsMail(News):
    def __init__(self, topic_xpath, link_xpath, source_xpath, date_xpath):
        self.url = "news.mail.ru"
        super().__init__(topic_xpath, link_xpath, source_xpath, date_xpath)

    @property
    def date(self):
        return super().date

    @date.setter
    def date(self, date):
        if type(date) == str and 'T' in date:
            self._date = datetime.date.fromisoformat(date.split('T')[0])
        else:
            self._date = datetime.datetime.now().date()