#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.crawler_requests import Crawler_Requests
from lib.douban_movie_entry_list import Douban_Movie_Entry_List
from lib.mixed_unicode_align import mixed_unicode_align
import os
import pickle

LIST_TYPE_COLLECT = 'collect'
LIST_TYPE_WISH = 'wish'
START_URL = 'https://movie.douban.com/people/{people_id}/{list_type}?start=0&sort=title&rating=all&filter=all&mode=list'

# set up sensitivy personal information
people_id = ''
proxy_list = [
]
from sensitive_info import *
# set up sensitivy personal information

def main():
    list_wish = Douban_Movie_Entry_List(
        start_url = START_URL.format(
            people_id = people_id,
            list_type = LIST_TYPE_WISH
        ),
        requester = Crawler_Requests(
            proxy_list = proxy_list,
            allow_request_without_proxy = True,
            sleep_time_range = (1, 2),
        ),
    )

    list_wish.fill_list()
    list_wish.inspect_list()

    for e in list_wish:
        print('{}{}'.format(
            mixed_unicode_align('.', '<', 80,
            e.get_title(), resolve_as_wide = ['…']
        ),
            e.get_release_date()
        ))

if (__name__ == '__main__'):
    main()
