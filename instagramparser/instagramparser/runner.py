from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagramparser import settings
from instagramparser.spiders.instagram import InstagramSpider
from instagramparser.spiders.instaphoto import InstaphotoSpider
import pymongo
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    (load_dotenv(dotenv_path))

LOGIN = os.getenv('LOGIN')
PSWD = os.getenv('PSWD')


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    mongo_uri = crawler_settings.get('MONGO_URI')
    client = pymongo.MongoClient(mongo_uri)
    mongo_db = crawler_settings.get('MONGO_DATABASE')
    db = client[mongo_db]
    collection = db['domashka__']
    res = collection.find()
    usernames = [user.get('username') for user in res]
    process = CrawlerProcess(settings=crawler_settings)
    #process.crawl(InstagramSpider, ['tarasen3306',], LOGIN, PSWD)
    process.crawl(InstaphotoSpider, usernames)
    process.start()
