import re
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pprint import pprint

SEARCH_STRING = 'Data Scientist'
PAGE_HH = 0

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15'}

CURRENCY_DICT = {}

def get_hh_response(search_string):
    url = 'https://hh.ru/search/vacancy'
    params = {
        'text': search_string,
        'page': PAGE_HH
    }
    return requests.get(url, params, headers=HEADERS)


def create_currency_dict():
    today = datetime.datetime.now().date()
    params = {'data_req': f'{today.day}/{today.month}/{today.year}'}
    response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params=params)
    bs_xml = BeautifulSoup(response.text, 'xml')
    for valute in bs_xml.find_all('Valute'):
        CURRENCY_DICT[valute.find('CharCode').text] = float(valute.Value.text.replace(',', '.'))
    CURRENCY_DICT['RUB'] = 1


def convert_compensation(compensation):
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
        min_max =  pattern.findall(compensation)
        if len(min_max) == 2:
            min_compensation = min_max[0]
            max_compensation = min_max[1]
        elif len(min_max) == 1:
            min_compensation = min_max[0]
    return [min_compensation, max_compensation, currency]


def get_page(get_url, search_string):
    response = get_hh_response('Data scientist')
    bs = BeautifulSoup(response.text, 'lxml')
    return bs


def get_vacancies(bs):
    vacancy_list = []
    all_vacancies = bs.find('div', {'class': 'vacancy-serp'})
    for elem in all_vacancies.contents:
        if 'data-qa' in elem.attrs and 'vacancy-serp__vacancy' in elem.attrs['data-qa']:
            position = elem.find('a', attrs={'class': 'bloko-link HH-LinkModifier'}).text
            company = elem.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
            city = elem.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
            compensation = elem.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            compensation_min, compensation_max, compensation_currency = convert_compensation(compensation)
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
    return vacancy_list, bs.find('a', {'data-qa': 'pager-next'}) and True


def vacancies_to_df(vacancy_list):
    return pd.DataFrame(vacancy_list)


def save_hh():
    have_page = True
    vacancy_list = []
    while have_page:
        bs = get_page(get_hh_response, SEARCH_STRING, )
        all_vacancies = bs.find('div', {'class': 'vacancy-serp'})
        vc_lst, have_page = get_vacancies(bs)
        vacancy_list.extend(vc_lst)
        global PAGE_HH
        PAGE_HH += 1
        time.sleep(2)
    df = vacancies_to_df(vacancy_list)
    df.compensation_min = df.compensation_min.astype(float)
    df.compensation_max = df.compensation_max.astype(float)
    df.to_pickle('df.bin')


def convert_currency(row):
    if row.compensation_min:
        row.compensation_min = row.compensation_min * CURRENCY_DICT[row.compensation_currency]
    if row.compensation_max:
        row.compensation_max = row.compensation_max * CURRENCY_DICT[row.compensation_currency]
    return row


def load_hh():
    create_currency_dict()
    #pprint(CURRENCY_DICT)
    df = pd.read_pickle('df.bin').fillna('')
    df = df.apply(convert_currency, axis=1)
    df.to_csv('hh_vacancies.csv')


if __name__ == '__main__':
    load_hh()
