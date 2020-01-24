# -*- coding: utf-8 -*-
import json
from typing import List
import scrapy
from scrapy.http import HtmlResponse
from instagramparser.items import InstagramPhotoItem
from scrapy.loader import ItemLoader


class InstaphotoSpider(scrapy.Spider):
    name = 'instaphoto'
    allowed_domains = ['instagram.com', 'cdninstagram.com',
                       'scontent-arn2-1.cdninstagram.com']
    start_urls = ['https://instagram.com/']

    def __init__(self, followers: List[str],  *args, **kwargs):
        self.followers = followers
        super().__init__(*args, **kwargs)

    def parse(self, response):
        for follower in self.followers:
            yield response.follow(f'{self.start_urls[0]}{follower}/?__a=1',
                                  callback=self.get_avatar_hd,
                                  cb_kwargs={'follower_name': follower})

    def get_avatar_hd(self, response: HtmlResponse, follower_name):
        js_data = json.loads(response.body)
        avatar_hd_url = js_data.get('graphql').get('user').get('profile_pic_url_hd')
        if avatar_hd_url:
            loader = ItemLoader(item=InstagramPhotoItem(),
                                response=response)
            loader.add_value('image_urls', [avatar_hd_url,])
            loader.add_value('follower_name', follower_name)
            item = loader.load_item()
            yield item
