from news_scraper.scraper import ScraperLenta, ScraperYandex, ScraperMail
from news_scraper.bd_converters import NewsMongoClient


def scraping_news(mongodb_client, yandex=True, mail=True, lenta=True):
    scrapers = []
    if yandex:
        scrapers.append(ScraperYandex())
    if mail:
        scrapers.append((ScraperMail()))
    if lenta:
        scrapers.append((ScraperLenta()))
    for scraper in scrapers:
        mongodb_client.insert_many(scraper.news_dict)


if __name__ == '__main__':
    mongodb_client = NewsMongoClient()
    scraping_news(mongodb_client)