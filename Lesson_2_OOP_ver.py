from abc import ABC, abstractmethod
import re
import random
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pprint import pprint


def create_currency_dict():
    currency_dict = {}
    today = datetime.datetime.now().date()
    url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    params = {'data_req': f'{today.day}/{today.month}/{today.year}'}
    response = requests.get(url, params=params)
    bs_xml = BeautifulSoup(response.text, 'xml')
    for currency in bs_xml.find_all('Valute'):
        currency_dict[currency.find('CharCode').text] = float(currency.Value.text.replace(',', '.'))
    currency_dict['RUB'] = 1
    return currency_dict


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


class VacancyParserBase(VacancyParserABC):

    @classmethod
    def convert_compensation(cls, compensation):
        min_compensation = None
        max_compensation = None
        currency = ''
        if compensation:
            compensation = compensation.text
            if 'руб' in compensation:
                currency = 'RUB'
            elif 'USD' in compensation:
                currency = 'USD'
            elif 'EUR' in compensation:
                currency = 'EUR'
            elif 'грн' in compensation:
                currency = 'UAH'
            compensation = compensation.replace(' ', '')
            compensation = compensation.replace(u'\xa0', '')
            pattern = re.compile(r'(\d+)')
            min_max = pattern.findall(compensation)
            if len(min_max) == 2:
                min_compensation = min_max[0]
                max_compensation = min_max[1]
                currency = 'RUB'
            elif len(min_max) == 1:
                min_compensation = min_max[0]
                currency = 'RUB'
        return [min_compensation, max_compensation, currency]

    def __init__(self, search_string,
                 user_agent_header):
        self.search_string = search_string
        self.user_agent_header = self.user_agent_dict[user_agent_header]
        self._vacancy_list = None

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

    def to_dataframe(self, currency_dict=None, save_csv=True):

        if self.vacancy_list:

            def convert_currency(row):
                if row.compensation_min:
                    row.compensation_min = row.compensation_min * currency_dict[row.compensation_currency]
                if row.compensation_max:
                    row.compensation_max = row.compensation_max * currency_dict[row.compensation_currency]
                return row

            df = pd.DataFrame(self.vacancy_list)
            df.compensation_min = df.compensation_min.astype(float)
            df.compensation_max = df.compensation_max.astype(float)
            df.fillna('', inplace=True)
            if currency_dict:
                df = df.apply(convert_currency, axis=1)
            if save_csv:
                now = str(datetime.datetime.now()).split('.')[0]
                time = str.join('', re.findall(r'(\d+)', now))
                csv_name = f'{self.__class__.__name__}_vacancies_{self.search_string.replace(" ", "-")}_{time}.csv'
                df.to_csv(csv_name)
            return df
        else:
            print('Нет вакансий')


class VacancyParserHH(VacancyParserBase):

    def __init__(self, search_string='Data Scientist',
                 url='https://hh.ru/search/vacancy',
                 user_agent_header='safari',
                 parse_all=True, timer=random.randint(2, 6)):
        super().__init__(search_string, user_agent_header)
        self.url = url
        self.parse_all = parse_all
        self.timer = timer
        self.__bs_pages = self.__get_pages()
        if self.__bs_pages:
            self._vacancy_list = self.__get_vacancy_bs()

    def __get_pages(self):

        def get_page(search_string, page_number):
            params = {
                'text': search_string,
                'page': page_number,
                'L_save_area': 'true',
            }
            response = requests.get(self.url, params, headers=self.user_agent_header)
            return BeautifulSoup(response.text, 'lxml')

        page_number = 0
        bs_list = []
        if self.parse_all:
            has_page = True
            while has_page:
                bs = get_page(self.search_string, page_number)
                bs_list.append(bs)
                has_page = bs.find('a', {'data-qa': 'pager-next'}) and True
                page_number += 1
        else:
            bs = get_page(self.search_string, page_number)
            bs_list.append(bs)
        return bs_list

    def __get_vacancy_bs(self):

        vacancy_list_all = []

        for bs in self.__bs_pages:

            vacancy_list_page = []
            vacancies = bs.find_all('div', {'data-qa': 'vacancy-serp__vacancy'})

            for elem in vacancies:
                position = elem.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                company = elem.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                city = elem.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                compensation = elem.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                compensation_min, compensation_max, compensation_currency = \
                    VacancyParserBase.convert_compensation(compensation)

                vacancy_list_page.append(
                    {
                        'position': position,
                        'company': company,
                        'city': city,
                        'compensation_min': compensation_min,
                        'compensation_max': compensation_max,
                        'compensation_currency': compensation_currency
                    }
                )
            vacancy_list_all.extend(vacancy_list_page)
            time.sleep(self.timer)
        return vacancy_list_all


class VacancyParserSJ(VacancyParserBase):

    def __init__(self, search_string='Data Scientist',
                 url='https://www.superjob.ru/vacancy/search/',
                 user_agent_header='chrome',
                 parse_all=True, timer=random.randint(2, 6)):
        super().__init__(search_string, user_agent_header)
        self.url = url
        self.parse_all = parse_all
        self.timer = timer
        self.__bs_pages = self.__get_pages()
        if self.__bs_pages:
            self._vacancy_list = self.__get_vacancy_bs()

    def __get_pages(self):

        def get_page(search_string):
            params = {
                'keywords': search_string,
            }
            url = requests.get(self.url, params, headers=self.user_agent_header).url
            self.url = url.split('=')[0] + '=1'

            def get_next_response(page_number):
                params = {
                    'page': page_number
                }
                response = requests.get(self.url, params=params, headers=self.user_agent_header)
                return BeautifulSoup(response.text, 'lxml')

            return get_next_response

        get_page_func = get_page(self.search_string)

        page_number = 1
        bs_list = []
        if self.parse_all:
            has_page = True
            while has_page:
                bs = get_page_func(page_number)
                bs_list.append(bs)
                has_page = bs.find('a', {'rel': 'next'}) and True
                page_number += 1
        else:
            bs = get_page_func(page_number)
            bs_list.append(bs)
        return bs_list

    def __get_vacancy_bs(self):

        vacancy_list_all = []

        for bs in self.__bs_pages:

            vacancy_list_page = []
            vacancies = bs.find_all('div', {'class': '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'})

            for elem in vacancies:
                position = elem.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).text
                company = elem.find('span',
                                    {
                                        'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _3e53o _15msI'})
                if company:
                    company = company.text
                city = elem.find('span',
                                 {'class': '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _3e53o'}).text.split(
                    ' • ')[1]
                compensation = elem.find('span',
                                         {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})
                compensation_min, compensation_max, compensation_currency = \
                    VacancyParserBase.convert_compensation(compensation)
                vacancy_list_page.append(
                    {
                        'position': position,
                        'company': company,
                        'city': city,
                        'compensation_min': compensation_min,
                        'compensation_max': compensation_max,
                        'compensation_currency': compensation_currency
                    }
                )
            pprint(vacancy_list_page)
            vacancy_list_all.extend(vacancy_list_page)
            time.sleep(self.timer)
        return vacancy_list_all


if __name__ == '__main__':
    currency_dict = create_currency_dict()
    parser = VacancyParserSJ(search_string='аналитик')
    parser.to_dataframe(currency_dict=currency_dict)
