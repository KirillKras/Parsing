import datetime
from urllib3.util.url import parse_url
import re
import requests
from bs4 import BeautifulSoup

# Функция получения курсов валют от ЦБ
def create_currency_dict():
    currency_dict = {}
    today = datetime.datetime.now().date()
    url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    params = {'data_req': f'{today.day}/{today.month}/{today.year}'}
    response = requests.get(url, params=params)
    if response.ok:
        bs_xml = BeautifulSoup(response.text, 'xml')
        for currency in bs_xml.find_all('Valute'):
            currency_dict[currency.find('CharCode').text] = float(currency.Value.text.replace(',', '.')) / float(currency.Nominal.text)
        currency_dict['RUB'] = 1
        return currency_dict
    return None


CURRENCY_DICT = create_currency_dict()


class Compensation(object):

    @classmethod
    def from_string(cls, compensation):
        min_compensation = None
        max_compensation = None
        currency = ''
        compensation = compensation
        if 'руб' in compensation:
            currency = 'RUB'
        elif 'USD' in compensation:
            currency = 'USD'
        elif 'EUR' in compensation:
            currency = 'EUR'
        elif 'грн' in compensation:
            currency = 'UAH'
        else:
            currency = 'RUB'
        compensation = compensation.replace(' ', '')
        compensation = compensation.replace(u'\xa0', '')
        pattern = re.compile(r'(\d+)')
        min_max = pattern.findall(compensation)
        if len(min_max) == 2:
            min_compensation = float(min_max[0])
            max_compensation = float(min_max[1])
        elif len(min_max) == 1:
            min_compensation = float(min_max[0])
        if CURRENCY_DICT:
            if currency != 'RUB':
                if min_compensation:
                    min_compensation *= CURRENCY_DICT[currency]
                if max_compensation:
                    max_compensation *= CURRENCY_DICT[currency]
                currency = 'RUB'
        return Compensation(min_compensation, max_compensation, currency)

    @staticmethod
    def __get_value(value):
        return round(float(value), 2) if value else None

    def __init__(self, min_compensation, max_compensation, currency):
        self.min_compensation = Compensation.__get_value(min_compensation)
        self.max_compensation = Compensation.__get_value(max_compensation)
        self.currency = currency


class Vacancy(object):

    @staticmethod
    def __get_position(position):
        return position.text if position else None

    @staticmethod
    def __get_company(company):
        return company.text if company else None

    @staticmethod
    def __get_city(city):
        if not city:
            return None
        city = city.text
        if ' • ' in city:
            city = city.split(' • ')[1]
        return city

    @staticmethod
    def __get_compensation(compensation):
        return Compensation.from_string(compensation.text) if compensation else Compensation(None, None, None)

    @staticmethod
    def __get_link(link):
        url, link = link
        link = link['href'] if link else None
        if link:
            link_parse = parse_url(link)
            if link_parse.hostname:
                link = f'{link_parse.scheme}://{link_parse.hostname}{link_parse.path}'
            else:
                link = f'{parse_url(url).scheme}://{parse_url(url).hostname}{link_parse.path}'
        return link

    def __init__(self, position, company, city,
                 compensation, link):
        self.position = Vacancy.__get_position(position)
        self.company = Vacancy.__get_company(company)
        self.city = Vacancy.__get_city(city)
        self.compensation = Vacancy.__get_compensation(compensation)
        self.link = Vacancy.__get_link(link)





