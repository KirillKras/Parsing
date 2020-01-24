# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from urllib.parse import urlencode, urljoin
import re
from typing import List
import scrapy
from scrapy.http import HtmlResponse
from instagramparser.items import InstagramparserItem, InstagramPhotoItem
from scrapy.loader import ItemLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    query_hash = 'c76146de99bb02f6415203be841dd25a'
    variables_base = {'fetch_mutual': 'true', 'include_reel': 'true', 'first': 100}
    opened = []

    def __init__(self, user_links: List[str], login: str, pswd: str, *args, **kwargs):
        self.user_links: List[str] = user_links
        self.login: str = login
        self.password: str = pswd
        super().__init__(*args, **kwargs)

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response)
        yield scrapy.FormRequest(
            url='https://www.instagram.com/accounts/login/ajax/',
            method='POST',
            callback=self.parse_users,
            formdata={'username': self.login, 'password': self.password},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_users(self, response: HtmlResponse):
        j_body: dict = json.loads(response.body)
        if j_body.get('authenticated'):
            for user in self.user_links:
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user,
                                      cb_kwargs={'user': user})

    def parse_user(self, response: HtmlResponse, user):
        user_id = self.fetch_user_id(response.text, user)
        user_vars = deepcopy(self.variables_base)
        user_vars.update({'id': user_id})
        yield response.follow(self.make_graphql_url(user_vars),
                              callback=self.parse_followers,
                              cb_kwargs={'user_vars': user_vars, 'user': user})

    def parse_followers(self, response: HtmlResponse, user_vars: dict, user):
        data: dict = json.loads(response.body)
        followers = data.get('data').get('user').get('edge_followed_by').get('edges')
        if followers:
            yield InstagramparserItem(
                user=user,
                followers=followers)
        if data.get('data').get('user').get('edge_followed_by').get('page_info').get('has_next_page'):
            user_vars.update({'after': data.get('data').get('user').get('edge_followed_by').get('page_info').get('end_cursor')})
            next_page = self.make_graphql_url(user_vars)
            yield response.follow(next_page, callback=self.parse_followers,
                                  cb_kwargs={'user_vars': user_vars, 'user': user})

    def fetch_csrf_token(self, response: HtmlResponse):
        matched = re.search(r'"csrf_token":"\w+"', response.text).group()
        return matched.split('\"')[3]

    def fetch_user_id(self, text, username):
        matched = re.search(r'{"id":"\d+","username":"%s"}' % username, text).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars):
        user_vars = str(user_vars).replace("'", '"')
        result = f'{self.graphql_url}query_hash={self.query_hash}&variables={user_vars}'
        return result
