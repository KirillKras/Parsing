from abc import ABC, abstractmethod
from urllib3.util.url import parse_url
import datetime
import json


class NewsABC(ABC):
    @property
    @abstractmethod
    def topic(self):
        """sdcsdc"""

    @property
    @abstractmethod
    def link(self):
        """"""

    @property
    @abstractmethod
    def source(self):
        """"""

    @property
    @abstractmethod
    def date(self):
        """"""


class News(NewsABC):
    @staticmethod
    def _get_attr(attr_xpath, base_attr):
        if attr_xpath:
            attr = attr_xpath[0]
            attr = attr.replace('\xa0', ' ')
            return attr
        return base_attr

    @staticmethod
    def _get_link(link):
        parsed_link = parse_url(link)
        if parsed_link.scheme and parsed_link.hostname:
            return f'{parsed_link.scheme}://{parsed_link.hostname}{parsed_link.path}'
        elif parsed_link.hostname:
            return f'https://{parsed_link.hostname}{parsed_link.path}'
        elif parsed_link.path:
            return parsed_link.path

    '''
    def __init__(self, topic_xpath, link_xpath, source_xpath, date_xpath,
                 base_topic='Заголовок новости не найден',
                 base_link='Ссылка на новость не найдена',
                 base_source=''):
        self._base_topic = base_topic
        self._base_link = base_link
        self._base_source = base_source
        self._base_date = datetime.datetime.now().date()
        self._topic = News._get_attr(topic_xpath, self._base_topic)
        self._link = News._get_attr(link_xpath, self._base_date)
        self._source = News._get_attr(source_xpath, self._base_source)
        self._date = News._get_attr(date_xpath, self._base_date)
    '''
    @property
    def topic(self):
        return self._topic

    @property
    def link(self):
        return self._link

    @property
    def source(self):
        return self._source

    @property
    def date(self):
        return self._date

    def __repr__(self):
        d = {
            'topic': self.topic,
            'link': self.link,
            'source': self.source,
            'date': self.date.__str__()
        }
        return d.__repr__()

    def __str__(self):
        return self.__repr__()


class NewsLenta(News):
    def __init__(self, topic_xpath, link_xpath):
        self.url = 'https://lenta.ru'
        self._topic = News._get_attr(topic_xpath, None)
        self._link = News._get_attr(link_xpath, None)
        self._link, self._source, self._date = self.__get_link_source_date(self._link)

    @staticmethod
    def __get_date_link_lenta(link):
        link_split = link.split('/')
        return datetime.date(year=int(link_split[-5]),
                             month=int(link_split[-4]),
                             day=int(link_split[-3]))

    @staticmethod
    def __get_date_link_moslenta(link):
        link_split = link.split('-')
        return datetime.date(year=int(link_split[-1].split('.')[0]),
                             month=int(link_split[-2]),
                             day=int(link_split[-3]))

    def __get_link_source_date(self, link):
        date = datetime.datetime.now().date()
        if not link:
            return link, parse_url(self.url).hostname, date
        link = News._get_link(link)
        parsed_link = parse_url(link)
        if parsed_link.hostname:
            if parsed_link.hostname == 'moslenta.ru':
                date = NewsLenta.__get_date_link_moslenta(link)
        else:
            link = self.url + link
            date = NewsLenta.__get_date_link_lenta(link)
        source = parse_url(link).hostname
        return link, source, date


class NewsYandex(News):
    def __init__(self, topic_xpath, link_xpath, source_xpath):
        self._topic = News._get_attr(topic_xpath, None)
        self._source = News._get_attr(source_xpath, None)
        self._link = News._get_attr(link_xpath, None)
        self._link = News._get_link(self._link)