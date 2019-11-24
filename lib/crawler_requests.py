#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Tuple
from urllib import parse
import fake_useragent as fua
import random
import requests
import time


class Crawler_Requests(object):
    def __init__(
        self, *,
        proxies: Dict[str, str] = {},
        headers: Dict[str, str] = {},
        cookies=requests.cookies.RequestsCookieJar(),
        proxy_list: List[Dict[str, str]] = [],
        allow_request_without_proxy=False,
        sleep_time_range: Tuple[int, int] = (1, 3),
        counter_limit_range: Tuple[int, int] = (50, 100),
    ):
        # because `refresh_identity()` will be called in the end of
        # constructor, the following things should be noted
        #
        # - `proxies` and `proxy_list` should not both been provided
        # - `headers` and `cookies` will be refreshed before actually been used
        #
        # these values should be passed into `refresh_identity()`
        # function if desired
        self._proxies = proxies
        self._headers = headers
        self._cookies = cookies
        self.__proxy_list = proxy_list
        self.__allow_request_without_proxy = allow_request_without_proxy
        self.__sleep_time_range = sleep_time_range
        self.__counter_limit_range = counter_limit_range
        self.__counter_limit = 0
        self.__counter = 0
        self.__fua = fua.UserAgent()
        self.refresh_identity()

    def get(self, *args, **kwargs) -> requests.models.Response:
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
        time.sleep(random.uniform(*self.__sleep_time_range))

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

    def refresh_identity(self, **kwargs) -> None:
        if ('proxies' in kwargs):
            self._proxies = kwargs['proxies']
        elif (len(self.__proxy_list) != 0):
            if (self.__allow_request_without_proxy):
                self._proxies = random.choice(self.__proxy_list + [{}])
            else:
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

        self.__counter_limit = random.randint(*self.__counter_limit_range)
        self.__counter = 0

    def set_proxy_list(self, proxy_list: List[Dict[str, str]]) -> None:
        self.__proxy_list = proxy_list

    def get_proxy_list(self) -> List[Dict[str, str]]:
        return self.__proxy_list

    def set_allow_request_without_proxy(self, allow_request_without_proxy: bool) -> None:
        self.__allow_request_without_proxy = allow_request_without_proxy

    def get_allow_request_without_proxy(self) -> bool:
        return self.__allow_request_without_proxy

    def set_headers_referer(self, referer: str) -> None:
        self._headers['Referer'] = referer

    def set_headers_user_agent(self, user_agent: str) -> None:
        self._headers['User-Agent'] = user_agent

    def set_sleep_time_range(self, sleep_time_range: Tuple[int, int]) -> None:
        self.__sleep_time_range = sleep_time_range

    def get_sleep_time_range(self) -> Tuple[int, int]:
        return self.__sleep_time_range

    def set_counter_limit_range(self, counter_limit_range: Tuple[int, int]) -> None:
        self.__counter_limit_range = counter_limit_range

    def get_counter_limit_range(self) -> Tuple[int, int]:
        return self.__counter_limit_range
