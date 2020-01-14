from news_scraper.scraper import ScraperLenta, ScraperYandex, ScraperMail
from bd_converters import MongoClient


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
    news_mongo_db = MongoClient(index_id='link', db_name='NewsScraper',
                                collection_name='newsCollection')
    scraping_news(news_mongo_db)