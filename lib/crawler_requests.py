#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fake_useragent import UserAgent
from typing import List, Dict, Tuple
from urllib import parse
import random
import requests
import time

class Crawler_Requests(object):
    def __init__(
        self, *,
        proxies = {},
        headers = {},
        cookies = requests.cookies.RequestsCookieJar(),
        proxy_list = [],
        sleep_time = (1, 5, ),
        counter_limit = 100,
    ):
        self._proxies = proxies
        self._headers = headers
        self._cookies = cookies
        self.__proxy_list = proxy_list
        self.__sleep_time = sleep_time
        self.__fua = UserAgent()
        self.__counter = 0
        self.__counter_limit = counter_limit
        self.refresh_identity()

    def get(self, *args, **kwargs):
        if (
            (self.__counter_limit != 0)
            and (self.__counter_limit <= self.__counter)
        ):
            self.refresh_identity()

        args_dict = {}
        if (('proxies' not in kwargs) and (len(self._proxies) != 0)):
            args_dict['proxies'] = self._proxies
        if (('headers' not in kwargs) and (len(self._headers) != 0)):
            args_dict['headers'] = self._headers
        if (('cookies' not in kwargs) and (len(self._cookies.items()) != 0)):
            args_dict['cookies'] = self._cookies

        page = requests.get(*args, **args_dict, **kwargs)
        self.__counter += 1
        time.sleep(
            random.random() * (self.__sleep_time[1] - self.__sleep_time[0])
            + self.__sleep_time[0]
        )

        if (
            ('Referer' not in self._headers)
            or (self._headers['Referer'] == '')
        ):
            urlparse = parse.urlparse(page.url)
            self.set_headers_referer(parse.urlunparse(
                (urlparse.scheme, urlparse.netloc, '', '', '', '')
            ))
        if (len(self._cookies.items()) == 0):
            self._cookies = page.cookies

        return page

    def refresh_identity(self, **kwargs):
        if ('proxies' in kwargs):
            self._proxies = kwargs['proxies']
        elif (len(self.__proxy_list) != 0):
            self._proxies = random.choice(self.__proxy_list)

        if (('headers' in kwargs) and ('Referer' in kwargs['headers'])):
            self.set_headers_referer(kwargs['headers']['Referer'])
        else:
            self._headers.pop('Referer', '')
        if (('headers' in kwargs) and ('User-Agent' in kwargs['headers'])):
            self.set_headers_user_agent(kwargs['headers']['User-Agent'])
        else:
            self.set_headers_user_agent(self.__fua.chrome)

        if ('cookies' in kwargs):
            self._cookies = kwargs['cookies']
        else:
            self._cookies.clear()

        self.__counter = 0

    def set_proxy_list(self, proxy_list: List[Dict[str, str]]):
        self.__proxy_list = proxy_list
    def get_proxy_list(self) -> List[Dict[str, str]]:
        return self.__proxy_list

    def set_headers_referer(self, referer: str):
        self._headers['Referer'] = referer
    def set_headers_user_agent(self, user_agent: str):
        self._headers['User-Agent'] = user_agent

    def set_sleep_time(self, sleep_time: Tuple[int, int]):
        self.__sleep_time = sleep_time
    def get_sleep_time(self) -> Tuple[int, int]:
        return self.__sleep_time

    def set_counter_limit(self, counter_limit: int):
        self.__counter_limit = counter_limit
    def get_counter_limit(self) -> int:
        return self.__counter_limit
