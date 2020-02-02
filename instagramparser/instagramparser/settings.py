# -*- coding: utf-8 -*-

# Scrapy settings for instagramparser project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from urllib.parse import quote_plus as quote
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
print(dotenv_path, os.getenv('PSWD'))

BOT_NAME = 'instagramparser'

SPIDER_MODULES = ['instagramparser.spiders']
NEWSPIDER_MODULE = 'instagramparser.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

LOG_ENABLED = True
LOG_LEVEL = 'ERROR' #INFO ERROR

IMAGES_STORE = '/Users/kosmosivanov/git-repo/Parsing/instagramparser/instagramparser/images'

MEDIA_ALLOW_REDIRECTS = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'instagramparser (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 6

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html

RETRY_HTTP_CODES = [429, ]

# SPIDER_MIDDLEWARES = {
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
#     'instagramparser.middlewares.TooManyRequestsRetryMiddleware': 100,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
   'instagramparser.middlewares.TooManyRequestsRetryMiddleware': 100,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'instagramparser.pipelines.InstagramPhotoPipeline': 200,
   'instagramparser.pipelines.MongoPipeline': 100,
}
MONGO_DATABASE = 'insta_followers'
SSL_CA_CERTS = '/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt'
MONGO_URI = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
    user=quote(os.getenv('MONGO_USER')),
    pw=quote(os.getenv('PSWD')),
    hosts=','.join([
        'rc1a-xg8zpggvbcedkqrm.mdb.yandexcloud.net:27018'
    ]),
    rs='rs01',
    auth_src=MONGO_DATABASE)


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
