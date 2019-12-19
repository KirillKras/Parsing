from abc import ABCMeta, abstractmethod
import re
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pprint import pprint


def create_currency_dict():
    currency_dict = {}
    today = datetime.datetime.now().date()
    params = {'data_req': f'{today.day}/{today.month}/{today.year}'}
    response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params=params)
    bs_xml = BeautifulSoup(response.text, 'xml')
    for valute in bs_xml.find_all('Valute'):
        currency_dict[valute.find('CharCode').text] = float(valute.Value.text.replace(',', '.'))
    currency_dict['RUB'] = 1
    return currency_dict


class VacancyParserMeta(metaclass=ABCMeta):

    @abstractmethod
    def get_page(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class VacancyParserBase(VacancyParserMeta):
    def get_page(self):
        pass

    def get_vacancies(self):
        pass

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
            elif 'грн.' in compensation:
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


class VacancyParserHH(VacancyParserBase):

    def __init__(self, search_string,
                 url='https://hh.ru/search/vacancy',
                 page=0):
        self.search_string = search_string
        self.url = url
        self.page = page
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.88 Safari/537.36'}

    def get_page(self):
        params = {
            'text': self.search_string,
            'page': self.page,
        }
        response = requests.get(self.url, params, headers=self.headers)
        self.page = BeautifulSoup(response.text, 'lxml')

    def get_vacancies(self):
        if self.page:
            vacancy_list = []
            all_vacancies = self.page.find('div', {'class': 'vacancy-serp'})
            for elem in all_vacancies.contents:
                if 'data-qa' in elem.attrs and 'vacancy-serp__vacancy' in elem.attrs['data-qa']:
                    position = elem.find('a', attrs={'class': 'bloko-link HH-LinkModifier'}).text
                    company = elem.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                    city = elem.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                    compensation = elem.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                    compensation_min, compensation_max, compensation_currency = \
                        VacancyParserBase.convert_compensation(compensation)
                    vacancy_list.append(
                        {
                            'position': position,
                            'company': company,
                            'city': city,
                            'compensation_min': compensation_min,
                            'compensation_max': compensation_max,
                            'compensation_currency': compensation_currency
                        }
                    )
            pprint(vacancy_list)
            return vacancy_list, self.page.find('a', {'data-qa': 'pager-next'}) and True
        else:
            print('Сначала необходимо получить страницу')