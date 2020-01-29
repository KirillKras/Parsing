import re
import pymongo
from pymongo.errors import DuplicateKeyError
import hashlib
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


SCROLL_PAUSE_TIME = 0.5

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = 'cian'
MONGO_COLLECTION = 'moscow_rent'
COLLECTION = pymongo.MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]


def clean_msisdn(msisdn):
    return re.sub(r'[^0-9]', '', msisdn)


def scroll_page(driver: webdriver.Chrome):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def click_buttons(driver):
    for msisdn_button in driver.find_elements_by_xpath('//button[contains(@class, "simplified-button")]'):
        driver.execute_script("arguments[0].click();", msisdn_button)


def get_id_msisdn_address(container):
    try:
        address = container.find_element_by_xpath('.//span[@itemprop="name" and @content]').get_attribute('content')
        msisdn = container.find_element_by_xpath('.//div[contains(@class, "simplified-text")]/span').get_attribute(
            'innerHTML')
        msisdn = clean_msisdn(msisdn)
        _id = hashlib.sha1(f'{msisdn} {address}'.encode('utf-8')).hexdigest()
    except Exception as e:
        print(e)
        return None, None, None
    return _id, msisdn, address


def mongo_insert(_id, msisdn, address):
    try:
        COLLECTION.insert_one({
            '_id': _id,
            'msisdn': msisdn,
            'address': address
        })
    except DuplicateKeyError:
        print('Дубликат')


def parse():
    page_number = 1
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    while page_number < 100:
        print(page_number)
        url = f'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p={page_number}&region=1&type=4'
        try:
            driver.get(url)
            print(driver.current_url)
            WebDriverWait(driver, 3)
            scroll_page(driver)
            click_buttons(driver)
        except Exception as e:
            print(e)
        for container in driver.find_elements_by_xpath('//div[contains(@class, "main-container")]'):
            _id, msisdn, address = get_id_msisdn_address(container)
            print(msisdn, address, _id)
            if _id:
                mongo_insert(_id, msisdn, address)

        page_number += 1
        # next_page =  WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        #     (By.XPATH, "//ul[@class='_93444fe79c--list--HEGFW']/li[2]/a")))


if __name__ == '__main__':
    parse()
