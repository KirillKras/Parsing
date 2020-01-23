from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagramparser import settings
from instagramparser.spiders.instagram import InstagramSpider

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
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, ['domashka__',], LOGIN, PSWD)
    process.start()