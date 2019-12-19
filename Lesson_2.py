import re
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pprint import pprint

SEARCH_STRING = 'аналитик'
PAGE_HH = 0
PAGE_SJ = 1
HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
CURRENCY_DICT = {}


def create_currency_dict():
    today = datetime.datetime.now().date()
    params = {'data_req': f'{today.day}/{today.month}/{today.year}'}
    response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params=params)
    bs_xml = BeautifulSoup(response.text, 'xml')
    for valute in bs_xml.find_all('Valute'):
        CURRENCY_DICT[valute.find('CharCode').text] = float(valute.Value.text.replace(',', '.'))
    CURRENCY_DICT['RUB'] = 1


create_currency_dict()


def get_hh_response(search_string):
    url = 'https://hh.ru/search/vacancy'
    params = {
        'text': search_string,
        'page': PAGE_HH,
    }
    return requests.get(url, params, headers=HEADERS)


def get_sj_response(search_string):
    url = 'https://www.superjob.ru/vacancy/search/'
    params = {
        'keywords': search_string,
    }
    url = requests.get(url, params, headers=HEADERS).url

    def get_next_response(_):
        params = {
            'page': PAGE_SJ
        }
        return requests.get(url.split('=')[0] + '=1', params=params, headers=HEADERS)

    return get_next_response


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
            currency = 'RUB'
        elif len(min_max) == 1:
            min_compensation = min_max[0]
            currency = 'RUB'
    return [min_compensation, max_compensation, currency]


def get_page(get_response):
    response = get_response(SEARCH_STRING)
    bs = BeautifulSoup(response.text, 'lxml')
    return bs


def get_hh_vacancies(bs):
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
    pprint(vacancy_list)
    return vacancy_list, bs.find('a', {'data-qa': 'pager-next'}) and True


def get_sj_vacancies(bs):
    vacancy_list = []
    for elem in bs.find_all('div', {'class': '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'}):
        position = elem.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).text
        company = elem.find('span',
            {'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _3e53o _15msI'})
        if company:
            company = company.text
        city = elem.find('span',
            {'class': '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _3e53o'}).text.split(' • ')[1]
        compensation = elem.find('span',
            {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})
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
    pprint(vacancy_list)
    return vacancy_list, bs.find('a', {'rel': 'next'}) and True


def convert_currency(row):
    if row.compensation_min:
        row.compensation_min = row.compensation_min * CURRENCY_DICT[row.compensation_currency]
    if row.compensation_max:
        row.compensation_max = row.compensation_max * CURRENCY_DICT[row.compensation_currency]
    return row


def get_hh():
    have_page = True
    vacancy_list = []

    while have_page:
        bs = get_page(get_hh_response)
        vc_lst, have_page = get_hh_vacancies(bs)
        vacancy_list.extend(vc_lst)
        global PAGE_HH
        PAGE_HH += 1
        time.sleep(2)

    df = pd.DataFrame(vacancy_list)
    df.compensation_min = df.compensation_min.astype(float)
    df.compensation_max = df.compensation_max.astype(float)
    df.fillna('', inplace=True)
    df = df.apply(convert_currency, axis=1)
    df.to_csv('hh_vacancies.csv')


def get_sj(search_string):
    global PAGE_SJ
    have_page = True
    vacancy_list = []
    sj_response_func = get_sj_response(search_string)

    while have_page:
        bs = get_page(sj_response_func)
        vc_lst, have_page = get_sj_vacancies(bs)
        vacancy_list.extend(vc_lst)
        PAGE_SJ += 1
        time.sleep(2)

    df = pd.DataFrame(vacancy_list)
    df.compensation_min = df.compensation_min.astype(float)
    df.compensation_max = df.compensation_max.astype(float)
    df.fillna('', inplace=True)
    df = df.apply(convert_currency, axis=1)
    df.to_csv('sj_vacancies.csv')


if __name__ == '__main__':
    get_hh()
