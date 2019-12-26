import requests
import datetime
import time
from pprint import pprint
from lxml import html
from urllib3.util.url import parse_url

print(datetime.datetime.fromtimestamp(1577362930))


def mail():
    mail_url = 'https://news.mail.ru'

    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
    }

    response = requests.get(mail_url, headers=headers)
    if response.ok:
        root = html.fromstring(response.text)
        items = root.xpath("(//span[@class='item__text'] | //span[@class='photo__title'])")
        for item in items:
            name = item.xpath('./text()')[0].replace('\xa0', '')
            link = item.xpath('ancestor::a[@href]/@href')[0]
            source = 'Новости Mail.RU'
            date = datetime.datetime.now().date()
            if not parse_url(link).hostname:
                link = mail_url + link
            response = requests.get(link, headers=headers)
            if response.ok:
                root = html.fromstring(response.text)
                source_xpath = root.xpath("//a[@class='article__param color_blue']/text()")
                date = root.xpath("//time[@class=' js-ago']/@datetime")[0]
                date = datetime.date.fromisoformat(date.split('T')[0])
                if source_xpath:
                    source = source_xpath[0]
            time.sleep(1)
            print(source, name, date, link)

def yandex():
    yandex_url = 'https://news.yandex.ru'

    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
    }

    response = requests.get(yandex_url, headers=headers)
    if response.ok:
        root = html.fromstring(response.text)
        items = root.xpath("//div[@class='card__body']")
        for item in items:
            name = item.xpath(".//span[@class='link link_pseudo card__link']/text()")[0]
            source = item.xpath(".//div[@class='card__status card__status_left']/a/text()")[0]
            link = item.xpath("./a/@href")[0]
            parsed_link = parse_url(link)
            link = f'{parsed_link.scheme}://{parsed_link.hostname}{parsed_link.path}'
            date = datetime.datetime.now().date()
            print(source, name, date, link)


def lenta():

    lenta_url = 'https://lenta.ru'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

    response = requests.get(lenta_url, headers=headers)

    if response.ok:
        root = html.fromstring(response.text)
        items = root.xpath("//div[@class='first-item'] | //div[@class='item']")

        for item in items:
            name = item.xpath(".//a[text()]/text()")[0]
            link = item.xpath(".//a[text()]/@href")[0]
            parsed_link = parse_url(link)
            if not parsed_link.hostname:
                link = lenta_url + link
                link_split = link.split('/')
                date = datetime.date(
                    year=int(link_split[-5]),
                    month=int(link_split[-4]),
                    day=int(link_split[-3]))
            else:
                link = f'{parsed_link.scheme}://{parsed_link.hostname}{parsed_link.path}'
                if parsed_link.hostname == 'moslenta.ru':
                    link_split = link.split('-')
                    date = datetime.date(
                        year=int(link_split[-1].split('.')[0]),
                        month=int(link_split[-2]),
                        day=int(link_split[-3])
                    )
                else:
                    date = datetime.datetime.now().date()
            source = parse_url(link).hostname
            print(source, name, link, date)

mail()