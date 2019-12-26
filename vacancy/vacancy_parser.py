from abc import ABC, abstractmethod
import re
import random
import datetime
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from vacancy.filters import filterHH, filterSJ
from vacancy.entity import Vacancy
from vacancy.bd_converters import VacancyMongoClient


# Абстрактный класс парсеров, декларирующий обязательный интерфейс
class VacancyParserABC(ABC):

    @property
    @abstractmethod
    def vacancy_list(self):
        """Read-only свойство - список собранных вакансий"""

    @property
    @abstractmethod
    def user_agent_dict(self):
        """Словарь User-Agent"""

    @abstractmethod
    def to_dataframe(self):
        """Гарантирует конвертацию результата в pandas.DataFrame"""

    @abstractmethod
    def to_mongodb(self, collection):
        """"""


# Базовый класс парсеров, реализующий словарь браузеров, функцию конвертации в pandas.DataFrame
class VacancyParserBase(VacancyParserABC):

    def __init__(self, search_string, url,
                 user_agent_header, filter,
                 parse_all, page_number, timer):
        self.search_string = search_string
        self.url = url
        self.user_agent_header = self.user_agent_dict[user_agent_header]
        self.parse_all = parse_all
        self.page_number = page_number
        self.filter = filter
        self.timer = timer
        self._vacancy_list = None
        self._bs_pages = None

    @property
    def user_agent_dict(self):
        return {'chrome': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) '},

                'safari': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
                                         'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15'}
                }

    @property
    def vacancy_list(self):
        return self._vacancy_list

    def _get_page(self):
        pass

    def _get_pages(self):
        bs_list = []
        bs = self._get_page()
        bs_list.append(bs)
        if self.parse_all:
            has_page = True
            while has_page:
                self.page_number += 1
                bs = self._get_page()
                bs_list.append(bs)
                has_page = bs.find(self.filter.next.tag, self.filter.next.attrs) and True
        return bs_list

    def _get_vacancy_bs(self):
        vacancy_list_all = []
        for bs in self._bs_pages:
            vacancy_list_page = []
            vacancies = bs.find_all(self.filter.vacancy.tag, self.filter.vacancy.attrs)
            for elem in vacancies:
                position = elem.find(self.filter.position.tag, self.filter.position.attrs)
                company = elem.find(self.filter.company.tag, self.filter.company.attrs)
                city = elem.find(self.filter.city.tag, self.filter.city.attrs)
                compensation = elem.find(self.filter.compensation.tag, self.filter.compensation.attrs)
                link = [self.url, elem.find(self.filter.link.tag, self.filter.link.attrs)]
                vacancy = Vacancy(position, company, city, compensation, link)
                vacancy_list_page.append(
                    {
                        'position': vacancy.position,
                        'company': vacancy.company,
                        'city': vacancy.city,
                        'min_compensation': vacancy.compensation.min_compensation,
                        'max_compensation': vacancy.compensation.max_compensation,
                        'currency': vacancy.compensation.currency,
                        'link': vacancy.link
                    }
                )
            #pprint(vacancy_list_page)
            vacancy_list_all.extend(vacancy_list_page)
            time.sleep(self.timer)
        return vacancy_list_all

    def to_dataframe(self, save_csv=True):
        if self.vacancy_list:
            df = pd.DataFrame(self.vacancy_list)
            df.fillna('', inplace=True)
            if save_csv:
                now = str(datetime.datetime.now()).split('.')[0]
                time = str.join('', re.findall(r'(\d+)', now))
                csv_name = f'{self.__class__.__name__}_vacancies_{self.search_string.replace(" ", "-")}_{time}.csv'
                df.to_csv(csv_name)
            return df
        else:
            print('Нет вакансий')

    def to_mongodb(self, vacancy_mongodb: VacancyMongoClient):
        vacancy_mongodb.insert_many(self.vacancy_list)


# Класс, реализующий парсер вакансий в HH
class VacancyParserHH(VacancyParserBase):

    def __init__(self, search_string='Data Scientist',
                 url='https://hh.ru/search/vacancy',
                 filter=filterHH,
                 user_agent_header='safari',
                 parse_all=True, timer=random.randint(2, 6)):
        self.page_number = 0
        super().__init__(search_string, url, user_agent_header, filter,
                         parse_all, self.page_number, timer)
        self._bs_pages = self._get_pages()
        if self._bs_pages:
            self._vacancy_list = self._get_vacancy_bs()

    def _get_page(self):
        params = {
            'text': self.search_string,
            'page': self.page_number,
            'L_save_area': 'true',
        }
        response = requests.get(self.url, params, headers=self.user_agent_header)
        return BeautifulSoup(response.text, 'lxml')


# Класс, реализующий парсер вакансий в SJ
class VacancyParserSJ(VacancyParserBase):

    def __init__(self, search_string='Data Scientist',
                 url='https://www.superjob.ru/vacancy/search/',
                 filter=filterSJ, user_agent_header='chrome',
                 parse_all=True, timer=random.randint(2, 6)):
        self.page_number = 1
        self.url = self.__get_url(url, search_string)
        super().__init__(search_string, url, user_agent_header, filter, parse_all, self.page_number, timer)
        self._bs_pages = self._get_pages()
        if self._bs_pages:
            self._vacancy_list = self._get_vacancy_bs()

    def __get_url(self, url, search_string):
        params = {
            'keywords': search_string,
        }
        url = requests.get(url, params,).url
        return url.split('=')[0] + '=1'

    def _get_page(self):
        params = {
            'page': self.page_number
        }
        response = requests.get(self.url, params=params, headers=self.user_agent_header)
        return BeautifulSoup(response.text, 'lxml')
