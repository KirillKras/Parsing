import datetime
import requests
from bs4 import BeautifulSoup
from jobparser.items import JobparserItem
from jobparser.spiders.hhru import HhruSpider
import pymongo
from pymongo.errors import DuplicateKeyError


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


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
            currency_dict[currency.find('CharCode').text] = float(currency.Value.text.replace(',', '.')) / float(
                currency.Nominal.text)
        currency_dict['RUB'] = 1
    return currency_dict


CURRENCY_DICT = create_currency_dict()


class JobparserPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        self.mongo_db = client.vacancy

    def open_spider(self, spider: HhruSpider):
        collection = self.mongo_db[spider.name]
        JobparserPipeline.__set_index(collection, 'url')

    def process_item(self, item: JobparserItem, spider: HhruSpider) -> JobparserItem:
        if item['name']:
            item['salary_min'] = JobparserPipeline.__get_salary_value(
                item['salary_min'], item['salary_currency'], item['salary_unit'])
            item['salary_max'] = JobparserPipeline.__get_salary_value(
                item['salary_max'], item['salary_currency'], item['salary_unit'])
            item['salary_currency'] = 'RUB' if item['salary_currency'] else None
            del item['salary_unit']
            collection = self.mongo_db[spider.name]
            try:
                collection.insert_one(item)
            except DuplicateKeyError:
                print('Дубль - не добавлено')
        return item

    @staticmethod
    def __get_salary_value(salary_value, salary_currency, salary_unit):
        salary_currency = salary_currency if salary_currency in CURRENCY_DICT else 'RUB'
        if salary_value and salary_currency:
            salary_value = float(salary_value) * CURRENCY_DICT[salary_currency]
            if salary_unit == 'YEAR':
                salary_value = salary_value / 12
            return round(salary_value, 2)
        return None

    @staticmethod
    def __set_index(collection, index_id: str):
        if f'{index_id}_1' not in collection.index_information():
            collection.create_index([(index_id, pymongo.ASCENDING)], unique=True)
